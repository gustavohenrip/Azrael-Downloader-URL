package com.pvdpro.controller;

import com.pvdpro.dto.AnalyzeRequest;
import com.pvdpro.dto.AnalyzeResponse;
import com.pvdpro.service.YtDlpService;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/videos")
public class VideoController {

    private final YtDlpService ytDlpService;

    public VideoController(YtDlpService ytDlpService) {
        this.ytDlpService = ytDlpService;
    }

    @PostMapping("/analyze")
    public AnalyzeResponse analyze(@Valid @RequestBody AnalyzeRequest request) {
        return ytDlpService.analyze(request.url());
    }
}
