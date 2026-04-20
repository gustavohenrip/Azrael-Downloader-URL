package com.pvdpro.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.pvdpro.config.AppProperties;
import com.pvdpro.dto.AnalyzeResponse;
import com.pvdpro.dto.VideoFormatDto;
import com.pvdpro.exception.ExternalToolException;
import com.pvdpro.model.YtDlpFormat;
import com.pvdpro.model.YtDlpMetadata;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.io.BufferedReader;
import java.nio.charset.StandardCharsets;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
public class YtDlpService {

    private final AppProperties properties;
    private final ObjectMapper objectMapper;

    public YtDlpService(AppProperties properties, ObjectMapper objectMapper) {
        this.properties = properties;
        this.objectMapper = objectMapper;
    }

    public AnalyzeResponse analyze(String url) {
        String targetUrl = requireUrl(url);
        String output = runAndCapture(List.of(
                properties.ytdlpCommand(),
                "--dump-single-json",
                "--no-download",
                "--no-playlist",
                "--no-warnings",
                "--no-color",
                targetUrl
        ));

        try {
            YtDlpMetadata metadata = objectMapper.readValue(output, YtDlpMetadata.class);
            return map(metadata);
        } catch (JsonProcessingException exception) {
            throw new ExternalToolException("Unable to parse yt-dlp output", exception);
        }
    }

    private AnalyzeResponse map(YtDlpMetadata metadata) {
        List<YtDlpFormat> formats = metadata.formats() == null ? List.of() : metadata.formats();
        List<YtDlpFormat> sortedFormats = formats.stream()
                .filter(this::isBrowserDownloadable)
                .sorted(Comparator
                        .comparing((YtDlpFormat format) -> format.height() == null ? -1 : format.height())
                        .reversed()
                        .thenComparing(format -> valueOrEmpty(format.ext()))
                        .thenComparing(format -> valueOrEmpty(format.formatId())))
                .toList();

        List<VideoFormatDto> formatDtos = sortedFormats.stream()
                .map(this::mapFormat)
                .toList();

        List<String> availableQualities = resolveQualities(sortedFormats);

        return new AnalyzeResponse(
                metadata.title(),
                metadata.duration(),
                metadata.viewCount(),
                metadata.uploader(),
                metadata.thumbnail(),
                formatDtos,
                availableQualities
        );
    }

    private boolean isBrowserDownloadable(YtDlpFormat format) {
        if (format == null || format.url() == null || format.url().isBlank()) {
            return false;
        }

        if (format.audioOnly()) {
            return false;
        }

        return !isNone(format.vcodec()) && !isNone(format.acodec());
    }

    private boolean isNone(String value) {
        return value == null || value.isBlank() || "none".equalsIgnoreCase(value);
    }

    private VideoFormatDto mapFormat(YtDlpFormat format) {
        return new VideoFormatDto(
                format.formatId(),
                format.height(),
                format.ext(),
                format.url(),
                format.effectiveSize(),
                format.formatNote(),
                format.vcodec(),
                format.acodec(),
                format.resolution(),
                format.fps()
        );
    }

    private List<String> resolveQualities(List<YtDlpFormat> formats) {
        Set<Integer> heights = formats.stream()
                .map(YtDlpFormat::height)
                .filter(Objects::nonNull)
                .collect(Collectors.toCollection(LinkedHashSet::new));

        List<String> qualities = new ArrayList<>();
        for (int standard : List.of(1080, 720, 480, 360, 240)) {
            if (heights.contains(standard)) {
                qualities.add(standard + "p");
            }
        }

        if (formats.stream().anyMatch(YtDlpFormat::audioOnly)) {
            qualities.add("audio-only");
        }

        if (qualities.isEmpty()) {
            List<Integer> sortedHeights = heights.stream()
                    .sorted(Comparator.reverseOrder())
                    .toList();
            for (Integer height : sortedHeights) {
                qualities.add(height + "p");
            }
            if (formats.stream().anyMatch(YtDlpFormat::audioOnly)) {
                qualities.add("audio-only");
            }
        }

        if (qualities.isEmpty()) {
            qualities.addAll(List.of("1080p", "720p", "480p", "360p", "240p", "audio-only"));
        }

        return qualities;
    }

    private String runAndCapture(List<String> command) {
        try {
            Process process = new ProcessBuilder(command)
                    .redirectErrorStream(true)
                    .start();

            StringBuilder output = new StringBuilder();
            Thread readerThread = new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        output.append(line).append(System.lineSeparator());
                    }
                } catch (IOException ignored) {
                }
            });
            readerThread.setDaemon(true);
            readerThread.start();

            boolean finished = process.waitFor(2, TimeUnit.MINUTES);
            if (!finished) {
                process.destroyForcibly();
                readerThread.join(2000);
                throw new ExternalToolException("yt-dlp analysis timed out");
            }

            readerThread.join(5000);

            if (process.exitValue() != 0) {
                throw new ExternalToolException(buildProcessError("yt-dlp analysis failed", output.toString()));
            }

            return output.toString();
        } catch (IOException exception) {
            throw new ExternalToolException("Unable to start yt-dlp", exception);
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            throw new ExternalToolException("yt-dlp analysis interrupted", exception);
        }
    }

    private String buildProcessError(String message, String output) {
        if (output == null || output.isBlank()) {
            return message;
        }
        return message + ": " + output.trim();
    }

    private String requireUrl(String url) {
        if (url == null || url.isBlank()) {
            throw new IllegalArgumentException("URL is required");
        }
        return url.trim();
    }

    private String valueOrEmpty(String value) {
        return value == null ? "" : value.toLowerCase(Locale.ROOT);
    }
}
