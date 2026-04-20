package com.pvdpro.controller;

import com.pvdpro.dto.DependencyStatusResponse;
import com.pvdpro.service.DependencyService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/system")
public class SystemController {

    private final DependencyService dependencyService;

    public SystemController(DependencyService dependencyService) {
        this.dependencyService = dependencyService;
    }

    @GetMapping("/dependencies")
    public DependencyStatusResponse dependencies() {
        return dependencyService.probe();
    }
}
