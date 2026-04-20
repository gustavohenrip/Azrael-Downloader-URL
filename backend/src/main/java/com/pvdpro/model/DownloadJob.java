package com.pvdpro.model;

import com.pvdpro.dto.DownloadStatusResponse;
import com.pvdpro.dto.DownloadUpdate;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.nio.file.Path;
import java.time.Instant;
import java.util.Locale;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

public class DownloadJob {

    private final String jobId;
    private final String sourceUrl;
    private final Path targetDirectory;
    private final Instant createdAt;
    private final Instant startedAt;
    private final CopyOnWriteArrayList<SseEmitter> emitters = new CopyOnWriteArrayList<>();
    private final AtomicReference<DownloadStatus> status = new AtomicReference<>(DownloadStatus.QUEUED);
    private final AtomicReference<Double> progress = new AtomicReference<>(0d);
    private final AtomicReference<String> message = new AtomicReference<>("Queued");
    private final AtomicReference<String> fileName = new AtomicReference<>();
    private final AtomicReference<Path> outputFile = new AtomicReference<>();
    private final AtomicReference<Process> process = new AtomicReference<>();
    private final AtomicBoolean cancelled = new AtomicBoolean(false);

    public DownloadJob(String jobId, String sourceUrl, Path targetDirectory) {
        this.jobId = jobId;
        this.sourceUrl = sourceUrl;
        this.targetDirectory = targetDirectory;
        this.createdAt = Instant.now();
        this.startedAt = this.createdAt;
    }

    public String getJobId() {
        return jobId;
    }

    public String getSourceUrl() {
        return sourceUrl;
    }

    public Path getTargetDirectory() {
        return targetDirectory;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public Instant getStartedAt() {
        return startedAt;
    }

    public Process getProcess() {
        return process.get();
    }

    public void setProcess(Process process) {
        this.process.set(process);
    }

    public boolean isCancelled() {
        return cancelled.get();
    }

    public void setCancelled(boolean cancelled) {
        this.cancelled.set(cancelled);
    }

    public void addEmitter(SseEmitter emitter) {
        emitters.add(emitter);
    }

    public void removeEmitter(SseEmitter emitter) {
        emitters.remove(emitter);
    }

    public void completeEmitters() {
        for (SseEmitter emitter : emitters) {
            try {
                emitter.complete();
            } catch (Exception ignored) {
            }
        }
        emitters.clear();
    }

    public void broadcast(DownloadUpdate update) {
        for (SseEmitter emitter : emitters) {
            try {
                emitter.send(SseEmitter.event().name(update.type()).data(update));
            } catch (Exception exception) {
                emitters.remove(emitter);
            }
        }
    }

    public DownloadStatus getStatus() {
        return status.get();
    }

    public void setStatus(DownloadStatus status) {
        this.status.set(status);
    }

    public Double getProgress() {
        return progress.get();
    }

    public void setProgress(double progress) {
        this.progress.set(Math.max(0d, Math.min(100d, progress)));
    }

    public String getMessage() {
        return message.get();
    }

    public void setMessage(String message) {
        this.message.set(message == null ? "" : message);
    }

    public String getFileName() {
        return fileName.get();
    }

    public void setFileName(String fileName) {
        this.fileName.set(fileName);
    }

    public Path getOutputFile() {
        return outputFile.get();
    }

    public void setOutputFile(Path outputFile) {
        this.outputFile.set(outputFile);
        if (outputFile != null) {
            this.fileName.set(outputFile.getFileName().toString());
        }
    }

    public boolean isTerminal() {
        return switch (status.get()) {
            case COMPLETED, FAILED, CANCELLED -> true;
            default -> false;
        };
    }

    public String statusLabel() {
        return status.get().name().toLowerCase(Locale.ROOT);
    }

    public String downloadUrl() {
        return fileName.get() == null ? null : "/api/downloads/" + jobId + "/file";
    }

    public DownloadUpdate update(String type) {
        return new DownloadUpdate(jobId, type, statusLabel(), progress.get(), message.get(), fileName.get(), downloadUrl());
    }

    public DownloadStatusResponse snapshot() {
        return new DownloadStatusResponse(jobId, statusLabel(), progress.get(), message.get(), fileName.get(), downloadUrl());
    }
}
