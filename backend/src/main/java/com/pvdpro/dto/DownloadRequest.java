package com.pvdpro.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record DownloadRequest(
        @NotBlank @Size(max = 2048) @Pattern(regexp = "^https?://.+") String url,
        @Size(max = 32) String quality,
        @Size(max = 16) String format,
        @Size(max = 128) String selectedFormatId,
        @Size(max = 512) String outputFolder
) {
}
