package com.pvdpro.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

@JsonInclude(JsonInclude.Include.NON_NULL)
public record VideoFormatDto(
        String formatId,
        Integer height,
        String ext,
        String url,
        Long filesize,
        String formatNote,
        String vcodec,
        String acodec,
        String resolution,
        Double fps
) {
}
