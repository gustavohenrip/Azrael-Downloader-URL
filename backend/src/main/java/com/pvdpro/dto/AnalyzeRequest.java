package com.pvdpro.dto;

import jakarta.validation.constraints.NotBlank;

public record AnalyzeRequest(
        @NotBlank String url
) {
}
