package com.pvdpro.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

import java.util.List;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record AnalyzeResponse(
        String title,
        Long durationSeconds,
        Long viewCount,
        String uploader,
        String thumbnailUrl,
        List<VideoFormatDto> formats,
        List<String> availableQualities
) {
}
