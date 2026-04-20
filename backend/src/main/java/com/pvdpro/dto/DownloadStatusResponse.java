package com.pvdpro.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record DownloadStatusResponse(
        String jobId,
        String status,
        Double progress,
        String message,
        String fileName,
        String downloadUrl
) {
}
