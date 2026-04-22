package com.pvdpro.service;

import com.pvdpro.config.AppProperties;
import com.pvdpro.dto.DownloadRequest;
import com.pvdpro.dto.DownloadStartResponse;
import com.pvdpro.dto.DownloadStatusResponse;
import com.pvdpro.dto.DownloadUpdate;
import com.pvdpro.exception.ResourceNotFoundException;
import com.pvdpro.model.DownloadJob;
import com.pvdpro.model.DownloadStatus;
import org.springframework.core.io.FileSystemResource;
import org.springframework.core.io.Resource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import jakarta.annotation.PreDestroy;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.NoSuchElementException;
import java.util.UUID;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class DownloadJobService {

    private static final Pattern PROGRESS_PATTERN = Pattern.compile("(\\d+(?:\\.\\d+)?)%");
    private static final Pattern FORMAT_ID_PATTERN = Pattern.compile("^[A-Za-z0-9_+\\-*\\[\\]=<>:./,]{1,128}$");
    private static final AtomicInteger THREAD_COUNTER = new AtomicInteger();

    private final AppProperties properties;
    private final FilePathResolver filePathResolver;
    private final ConcurrentMap<String, DownloadJob> jobs = new ConcurrentHashMap<>();
    private final ExecutorService executorService;

    public DownloadJobService(AppProperties properties, FilePathResolver filePathResolver) {
        this.properties = properties;
        this.filePathResolver = filePathResolver;
        this.executorService = new ThreadPoolExecutor(
                0, 4, 60L, TimeUnit.SECONDS,
                new ArrayBlockingQueue<>(16),
                runnable -> {
                    Thread thread = new Thread(runnable);
                    thread.setDaemon(true);
                    thread.setName("download-job-" + THREAD_COUNTER.incrementAndGet());
                    return thread;
                },
                new ThreadPoolExecutor.CallerRunsPolicy()
        );
    }

    public DownloadStartResponse start(DownloadRequest request) {
        String sourceUrl = requireUrl(request.url());
        Path targetDirectory = filePathResolver.resolveFolder(request.outputFolder());
        String jobId = UUID.randomUUID().toString();

        DownloadJob job = new DownloadJob(jobId, sourceUrl, targetDirectory);
        jobs.put(jobId, job);

        executorService.submit(() -> execute(job, request));

        return new DownloadStartResponse(jobId, job.statusLabel(), "Download queued");
    }

    public SseEmitter openStream(String jobId) {
        DownloadJob job = getJob(jobId);
        SseEmitter emitter = new SseEmitter(properties.emitterTimeout().toMillis());
        job.addEmitter(emitter);

        emitter.onCompletion(() -> job.removeEmitter(emitter));
        emitter.onTimeout(() -> job.removeEmitter(emitter));
        emitter.onError(throwable -> job.removeEmitter(emitter));

        sendSnapshot(job, emitter);
        if (job.isTerminal()) {
            emitter.complete();
        }

        return emitter;
    }

    public DownloadStatusResponse getStatus(String jobId) {
        return getJob(jobId).snapshot();
    }

    public void cancel(String jobId) {
        DownloadJob job = getJob(jobId);
        if (job.isTerminal()) {
            return;
        }

        job.setCancelled(true);
        Process process = job.getProcess();
        if (process != null && process.isAlive()) {
            process.destroy();
            try {
                if (!process.waitFor(3, TimeUnit.SECONDS)) {
                    process.destroyForcibly();
                }
            } catch (InterruptedException exception) {
                Thread.currentThread().interrupt();
                process.destroyForcibly();
            }
        }

        job.setStatus(DownloadStatus.CANCELLED);
        job.setProgress(0d);
        job.setMessage("Download cancelled by user");
        broadcast(job, job.update("cancelled"));
        job.completeEmitters();
    }

    public ResponseEntity<Resource> downloadFile(String jobId) {
        DownloadJob job = getJob(jobId);
        Path file = resolveCompletedFile(job);
        if (file == null || !Files.exists(file)) {
            throw new ResourceNotFoundException("Downloaded file not found");
        }

        try {
            Resource resource = new FileSystemResource(file);
            String contentType = Files.probeContentType(file);
            HttpHeaders headers = new HttpHeaders();
            headers.setContentDisposition(ContentDisposition.attachment()
                    .filename(file.getFileName().toString(), StandardCharsets.UTF_8)
                    .build());
            headers.setContentLength(Files.size(file));
            headers.setContentType(contentType == null ? MediaType.APPLICATION_OCTET_STREAM : MediaType.parseMediaType(contentType));
            return ResponseEntity.ok()
                    .headers(headers)
                    .body(resource);
        } catch (IOException exception) {
            throw new IllegalStateException("Unable to stream downloaded file", exception);
        }
    }

    @PreDestroy
    public void shutdown() {
        executorService.shutdownNow();
    }

    private void execute(DownloadJob job, DownloadRequest request) {
        try {
            job.setStatus(DownloadStatus.RUNNING);
            job.setProgress(0d);
            job.setMessage("Starting download");
            broadcast(job, job.update("snapshot"));

            DownloadPlan plan = buildPlan(request);
            if (plan.warningMessage() != null) {
                job.setMessage(plan.warningMessage());
                broadcast(job, job.update("log"));
            }

            List<String> command = buildCommand(job, request, plan);
            ProcessBuilder builder = new ProcessBuilder(command);
            builder.directory(job.getTargetDirectory().toFile());
            builder.redirectErrorStream(true);

            Process process = builder.start();
            job.setProcess(process);
            job.setMessage("Download running");
            broadcast(job, job.update("snapshot"));

            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    handleOutputLine(job, line);
                    if (job.isCancelled()) {
                        break;
                    }
                }
            }

            int exitCode = process.waitFor();
            if (job.isCancelled()) {
                finalizeCancelled(job);
                return;
            }

            Path completedFile = resolveCompletedFile(job);
            if (exitCode == 0 || completedFile != null) {
                if (completedFile != null) {
                    job.setOutputFile(completedFile);
                }
                job.setStatus(DownloadStatus.COMPLETED);
                job.setProgress(100d);
                job.setMessage(exitCode == 0 ? "Download completed" : "Download completed with warnings");
                broadcast(job, job.update("completed"));
                job.completeEmitters();
                return;
            }

            job.setStatus(DownloadStatus.FAILED);
            job.setMessage("Download failed");
            broadcast(job, job.update("failed"));
            job.completeEmitters();
        } catch (IOException exception) {
            if (job.isCancelled()) {
                finalizeCancelled(job);
                return;
            }
            job.setStatus(DownloadStatus.FAILED);
            job.setMessage(exception.getMessage());
            broadcast(job, job.update("failed"));
            job.completeEmitters();
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            if (job.isCancelled()) {
                finalizeCancelled(job);
                return;
            }
            job.setStatus(DownloadStatus.FAILED);
            job.setMessage("Download interrupted");
            broadcast(job, job.update("failed"));
            job.completeEmitters();
        } finally {
            job.setProcess(null);
        }
    }

    private void finalizeCancelled(DownloadJob job) {
        job.setStatus(DownloadStatus.CANCELLED);
        job.setProgress(0d);
        job.setMessage("Download cancelled by user");
        broadcast(job, job.update("cancelled"));
        job.completeEmitters();
    }

    private List<String> buildCommand(DownloadJob job, DownloadRequest request, DownloadPlan plan) {
        List<String> command = new ArrayList<>();
        command.add(properties.ytdlpCommand());
        command.add("--no-color");
        command.add("--newline");
        command.add("--no-playlist");
        command.add("--output");
        command.add(job.getTargetDirectory().resolve("%(title).200B.%(ext)s").toString());
        command.add("--print");
        command.add("after_move:filepath");
        command.add("--format");
        command.add(plan.formatSelector());
        command.addAll(plan.extraArgs());
        command.add("--");
        command.add(requireUrl(request.url()));
        return command;
    }

    private void handleOutputLine(DownloadJob job, String line) {
        String trimmed = line == null ? "" : line.trim();
        if (trimmed.isEmpty()) {
            return;
        }

        Matcher matcher = PROGRESS_PATTERN.matcher(trimmed);
        if (matcher.find()) {
            double progress = Double.parseDouble(matcher.group(1));
            job.setStatus(DownloadStatus.RUNNING);
            job.setProgress(progress);
            job.setMessage("Downloading... " + String.format(Locale.US, "%.1f%%", progress));
            broadcast(job, job.update("progress"));
            return;
        }

        Path capturedPath = capturePath(trimmed);
        if (capturedPath != null) {
            job.setOutputFile(capturedPath);
            job.setMessage("Saved file path detected");
            broadcast(job, job.update("log"));
            return;
        }

        job.setMessage(trimmed);
        broadcast(job, job.update("log"));
    }

    private Path capturePath(String line) {
        if (line.startsWith("[")) {
            return null;
        }

        try {
            Path candidate = Path.of(line);
            if (Files.exists(candidate) && Files.isRegularFile(candidate)) {
                return candidate.toAbsolutePath().normalize();
            }
        } catch (Exception ignored) {
        }

        return null;
    }

    private DownloadPlan buildPlan(DownloadRequest request) {
        String selectedFormatId = trimToNull(request.selectedFormatId());
        String quality = normalizeOrDefault(request.quality(), "720p");
        String format = normalizeOrDefault(request.format(), "mp4");

        if (selectedFormatId != null) {
            if (!FORMAT_ID_PATTERN.matcher(selectedFormatId).matches()) {
                throw new IllegalArgumentException("Invalid format ID");
            }
            return new DownloadPlan(selectedFormatId, List.of(), null);
        }

        if ("audio-only".equalsIgnoreCase(quality)) {
            return switch (format.toLowerCase(Locale.ROOT)) {
                case "mp3" -> new DownloadPlan("bestaudio[ext=webm]/bestaudio[ext=m4a]/bestaudio/best",
                        List.of("--extract-audio", "--audio-format", "mp3"), null);
                case "m4a" -> new DownloadPlan("bestaudio[ext=m4a]/bestaudio/best",
                        List.of("--extract-audio", "--audio-format", "m4a"), null);
                case "wav" -> new DownloadPlan("bestaudio/best",
                        List.of("--extract-audio", "--audio-format", "wav"), null);
                case "flac" -> new DownloadPlan("bestaudio/best",
                        List.of("--extract-audio", "--audio-format", "flac"), null);
                default -> new DownloadPlan("bestaudio/best",
                        List.of("--extract-audio", "--audio-format", "mp3"),
                        "Video format selected for audio-only. Converting to MP3.");
            };
        }

        int height = parseHeight(quality);
        return switch (format.toLowerCase(Locale.ROOT)) {
            case "mp4" -> new DownloadPlan(
                    "best[height<=" + height + "][ext=mp4]/best[height<=" + height + "][vcodec^=avc]/best[height<=" + height + "]/best",
                    List.of("--merge-output-format", "mp4"),
                    null
            );
            case "webm" -> new DownloadPlan(
                    "best[height<=" + height + "][ext=webm]/best[height<=" + height + "]/best",
                    List.of("--merge-output-format", "webm"),
                    null
            );
            case "mkv" -> new DownloadPlan(
                    "best[height<=" + height + "][ext=mkv]/best[height<=" + height + "]/best",
                    List.of("--merge-output-format", "mkv"),
                    null
            );
            default -> new DownloadPlan(
                    "best[height<=" + height + "][ext=mp4]/best[height<=" + height + "]/best",
                    List.of("--merge-output-format", "mp4"),
                    "Audio format selected for video. Converting to MP4."
            );
        };
    }

    private int parseHeight(String quality) {
        String normalized = trimToNull(quality);
        if (normalized == null) {
            return 720;
        }
        if ("audio-only".equalsIgnoreCase(normalized)) {
            return 720;
        }
        try {
            return Integer.parseInt(normalized.replace("p", ""));
        } catch (NumberFormatException exception) {
            return 720;
        }
    }

    private String normalizeOrDefault(String value, String fallback) {
        String trimmed = trimToNull(value);
        return trimmed == null ? fallback : trimmed;
    }

    private String trimToNull(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }

    private String requireUrl(String url) {
        String trimmed = trimToNull(url);
        if (trimmed == null) {
            throw new IllegalArgumentException("URL is required");
        }
        try {
            URI uri = URI.create(trimmed);
            String scheme = uri.getScheme();
            if (!"http".equals(scheme) && !"https".equals(scheme)) {
                throw new IllegalArgumentException("URL must use http or https");
            }
            if (uri.getHost() == null || uri.getHost().isBlank()) {
                throw new IllegalArgumentException("URL must have a valid host");
            }
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Invalid URL: " + e.getMessage());
        }
        return trimmed;
    }

    private void broadcast(DownloadJob job, DownloadUpdate update) {
        job.broadcast(update);
    }

    private void sendSnapshot(DownloadJob job, SseEmitter emitter) {
        try {
            emitter.send(SseEmitter.event().name("snapshot").data(job.snapshot()));
        } catch (IOException exception) {
            job.removeEmitter(emitter);
            throw new IllegalStateException("Unable to stream download status", exception);
        }
    }

    private DownloadJob getJob(String jobId) {
        DownloadJob job = jobs.get(jobId);
        if (job == null) {
            throw new NoSuchElementException("Unknown download job: " + jobId);
        }
        return job;
    }

    private Path resolveCompletedFile(DownloadJob job) {
        Path currentFile = job.getOutputFile();
        if (currentFile != null && Files.exists(currentFile)) {
            return currentFile;
        }

        String fileName = job.getFileName();
        if (fileName != null) {
            Path candidate = job.getTargetDirectory().resolve(fileName);
            if (Files.exists(candidate)) {
                return candidate;
            }
        }

        try {
            try (var stream = Files.list(job.getTargetDirectory())) {
                return stream
                        .filter(Files::isRegularFile)
                        .map(this::withModifiedTime)
                        .filter(entry -> entry.getValue().isAfter(job.getStartedAt().minusSeconds(10)))
                        .max(Comparator.comparing(Map.Entry::getValue))
                        .map(Map.Entry::getKey)
                        .orElse(null);
            }
        } catch (IOException exception) {
            return null;
        }
    }

    private Map.Entry<Path, Instant> withModifiedTime(Path path) {
        try {
            return Map.entry(path, Files.getLastModifiedTime(path).toInstant());
        } catch (IOException exception) {
            return Map.entry(path, Instant.EPOCH);
        }
    }

    private record DownloadPlan(String formatSelector, List<String> extraArgs, String warningMessage) {
    }
}
