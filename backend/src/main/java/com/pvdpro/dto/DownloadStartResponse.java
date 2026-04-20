package com.pvdpro.dto;

public record DownloadStartResponse(
        String jobId,
        String status,
        String message
) {
}
