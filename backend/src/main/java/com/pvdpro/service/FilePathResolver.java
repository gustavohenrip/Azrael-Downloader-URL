package com.pvdpro.service;

import com.pvdpro.config.AppProperties;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@Service
public class FilePathResolver {

    private final Path downloadRoot;

    public FilePathResolver(AppProperties properties) {
        this.downloadRoot = Path.of(properties.downloadRoot()).toAbsolutePath().normalize();
    }

    public Path resolveFolder(String relativeFolder) {
        Path target = downloadRoot;
        if (relativeFolder != null && !relativeFolder.isBlank()) {
            Path candidate = downloadRoot.resolve(relativeFolder.trim()).normalize();
            if (!candidate.startsWith(downloadRoot)) {
                throw new IllegalArgumentException("Output folder must stay inside the configured storage root");
            }
            target = candidate;
        }

        try {
            Files.createDirectories(target);
            return target;
        } catch (IOException exception) {
            throw new IllegalStateException("Unable to create the storage directory", exception);
        }
    }
}
