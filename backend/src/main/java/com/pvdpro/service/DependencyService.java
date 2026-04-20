package com.pvdpro.service;

import com.pvdpro.config.AppProperties;
import com.pvdpro.dto.DependencyStatusResponse;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

@Service
public class DependencyService {

    private final AppProperties properties;

    public DependencyService(AppProperties properties) {
        this.properties = properties;
    }

    public DependencyStatusResponse probe() {
        boolean ytDlpAvailable = isAvailable(properties.ytdlpCommand(), "--version");
        boolean ffmpegAvailable = isAvailable(properties.ffmpegCommand(), "-version");
        boolean ready = ytDlpAvailable;
        String message = ready ? "yt-dlp ready." : "Install yt-dlp.";
        return new DependencyStatusResponse(ytDlpAvailable, ffmpegAvailable, ready, message);
    }

    private boolean isAvailable(String command, String... arguments) {
        try {
            Process process = new ProcessBuilder(buildCommand(command, arguments))
                    .redirectErrorStream(true)
                    .start();
            boolean finished = process.waitFor(5, TimeUnit.SECONDS);
            if (!finished) {
                process.destroyForcibly();
                return false;
            }
            return process.exitValue() == 0;
        } catch (IOException exception) {
            return false;
        } catch (InterruptedException exception) {
            Thread.currentThread().interrupt();
            return false;
        }
    }

    private static String[] buildCommand(String command, String... arguments) {
        String[] values = new String[1 + arguments.length];
        values[0] = command;
        System.arraycopy(arguments, 0, values, 1, arguments.length);
        return values;
    }
}
