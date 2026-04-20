package com.pvdpro.dto;

public record DependencyStatusResponse(
        boolean ytDlpAvailable,
        boolean ffmpegAvailable,
        boolean ready,
        String message
) {
}
