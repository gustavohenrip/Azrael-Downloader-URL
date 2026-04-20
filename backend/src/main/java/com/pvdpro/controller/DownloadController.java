package com.pvdpro.controller;

import com.pvdpro.dto.DownloadRequest;
import com.pvdpro.dto.DownloadStartResponse;
import com.pvdpro.dto.DownloadStatusResponse;
import com.pvdpro.service.DownloadJobService;
import jakarta.validation.Valid;
import org.springframework.core.io.Resource;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@RequestMapping("/api/downloads")
public class DownloadController {

    private final DownloadJobService downloadJobService;

    public DownloadController(DownloadJobService downloadJobService) {
        this.downloadJobService = downloadJobService;
    }

    @PostMapping
    public DownloadStartResponse start(@Valid @RequestBody DownloadRequest request) {
        return downloadJobService.start(request);
    }

    @GetMapping("/{jobId}")
    public DownloadStatusResponse status(@PathVariable String jobId) {
        return downloadJobService.getStatus(jobId);
    }

    @GetMapping("/{jobId}/events")
    public SseEmitter stream(@PathVariable String jobId) {
        return downloadJobService.openStream(jobId);
    }

    @PostMapping("/{jobId}/cancel")
    public ResponseEntity<Void> cancel(@PathVariable String jobId) {
        downloadJobService.cancel(jobId);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/{jobId}/file")
    public ResponseEntity<Resource> download(@PathVariable String jobId) {
        return downloadJobService.downloadFile(jobId);
    }
}
