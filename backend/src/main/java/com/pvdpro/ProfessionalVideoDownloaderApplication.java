package com.pvdpro;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

@SpringBootApplication
@ConfigurationPropertiesScan
public class ProfessionalVideoDownloaderApplication {

    public static void main(String[] args) {
        SpringApplication.run(ProfessionalVideoDownloaderApplication.class, args);
    }
}
