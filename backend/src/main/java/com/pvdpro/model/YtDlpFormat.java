package com.pvdpro.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public record YtDlpFormat(
        @JsonProperty("format_id") String formatId,
        @JsonProperty("format_note") String formatNote,
        @JsonProperty("url") String url,
        Integer height,
        String ext,
        @JsonProperty("filesize") Long filesize,
        @JsonProperty("filesize_approx") Long filesizeApprox,
        String vcodec,
        String acodec,
        String resolution,
        Double fps
) {

    public Long effectiveSize() {
        return filesize != null ? filesize : filesizeApprox;
    }

    public boolean audioOnly() {
        return height == null || "none".equalsIgnoreCase(vcodec);
    }
}
