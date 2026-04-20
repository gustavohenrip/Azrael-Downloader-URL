package com.pvdpro.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.time.Duration;

@ConfigurationProperties(prefix = "app")
public record AppProperties(
        String downloadRoot,
        String ytdlpCommand,
        String ffmpegCommand,
        String frontendOrigin,
        Duration emitterTimeout
) {

    public AppProperties {
        downloadRoot = defaultIfBlank(downloadRoot, "./storage/downloads");
        ytdlpCommand = defaultIfBlank(ytdlpCommand, "yt-dlp");
        ffmpegCommand = defaultIfBlank(ffmpegCommand, "ffmpeg");
        frontendOrigin = defaultIfBlank(frontendOrigin, "http://localhost:4200");
        emitterTimeout = emitterTimeout == null ? Duration.ofMinutes(30) : emitterTimeout;
    }

    private static String defaultIfBlank(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }
}
