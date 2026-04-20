package com.pvdpro.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record YtDlpMetadata(
        @JsonProperty("title") String title,
        @JsonProperty("duration") Long duration,
        @JsonProperty("view_count") Long viewCount,
        @JsonProperty("uploader") String uploader,
        @JsonProperty("thumbnail") String thumbnail,
        @JsonProperty("formats") List<YtDlpFormat> formats
) {
}
