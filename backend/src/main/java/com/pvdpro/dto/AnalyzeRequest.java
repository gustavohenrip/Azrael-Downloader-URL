package com.pvdpro.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public record AnalyzeRequest(
        @NotBlank @Size(max = 2048) @Pattern(regexp = "^https?://.+") String url
) {
}
