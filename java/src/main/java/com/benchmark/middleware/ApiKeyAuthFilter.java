package com.benchmark.middleware;

import jakarta.servlet.*;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * API Key Authentication Filter
 *
 * @author Benchmark Team
 */
@Slf4j
@Component
@Order(1)
public class ApiKeyAuthFilter implements Filter {

    @Value("${api.key}")
    private String apiKey;

    private static final String API_KEY_HEADER = "X-API-Key";

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;

        String requestPath = httpRequest.getRequestURI();

        // Skip health check and actuator endpoints
        if (requestPath.startsWith("/actuator") || requestPath.equals("/health")) {
            chain.doFilter(request, response);
            return;
        }

        // Skip OpenAPI documentation
        if (requestPath.startsWith("/v3/api-docs") || requestPath.startsWith("/swagger-ui")) {
            chain.doFilter(request, response);
            return;
        }

        // Get API key from header
        String requestApiKey = httpRequest.getHeader(API_KEY_HEADER);

        // Validate API key
        if (requestApiKey == null || requestApiKey.isEmpty()) {
            log.warn("Missing API key in request to: {}", requestPath);
            sendErrorResponse(httpResponse, HttpServletResponse.SC_UNAUTHORIZED, "Missing API key");
            return;
        }

        if (!apiKey.equals(requestApiKey)) {
            log.warn("Invalid API key in request to: {}", requestPath);
            sendErrorResponse(httpResponse, HttpServletResponse.SC_UNAUTHORIZED, "Invalid API key");
            return;
        }

        // API key is valid, proceed with request
        chain.doFilter(request, response);
    }

    private void sendErrorResponse(HttpServletResponse response, int status, String message) throws IOException {
        response.setStatus(status);
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        response.getWriter().write(String.format(
                "{\"code\":%d,\"message\":\"%s\",\"data\":null}",
                status == HttpServletResponse.SC_UNAUTHORIZED ? 401 : status,
                message
        ));
    }
}
