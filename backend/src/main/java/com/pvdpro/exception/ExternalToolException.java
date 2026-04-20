package com.pvdpro.exception;

public class ExternalToolException extends RuntimeException {

    public ExternalToolException(String message) {
        super(message);
    }

    public ExternalToolException(String message, Throwable cause) {
        super(message, cause);
    }
}
