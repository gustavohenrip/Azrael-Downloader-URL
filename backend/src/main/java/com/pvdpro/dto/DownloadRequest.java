package com.pvdpro.dto;

import jakarta.validation.constraints.NotBlank;

public record DownloadRequest(
        @NotBlank String url,
        String quality,
        String format,
        String selectedFormatId,
        String outputFolder
) {
}
