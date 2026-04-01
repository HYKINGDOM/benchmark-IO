# Build stage
FROM gradle:8.5-jdk21-alpine AS build

WORKDIR /app

# Copy Gradle files
COPY build.gradle settings.gradle ./
COPY gradle ./gradle

# Download dependencies
RUN gradle dependencies --no-daemon || true

# Copy source code
COPY src ./src

# Build application
RUN gradle clean build -x test --no-daemon

# Runtime stage
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Install necessary packages
RUN apk add --no-cache curl

# Create non-root user
RUN addgroup -S benchmark && adduser -S benchmark -G benchmark

# Create temp directory for exports
RUN mkdir -p /tmp/benchmark-exports && chown -R benchmark:benchmark /tmp/benchmark-exports

# Copy JAR from build stage
COPY --from=build /app/build/libs/benchmark-java.jar app.jar

# Change ownership
RUN chown -R benchmark:benchmark /app

# Switch to non-root user
USER benchmark

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/actuator/health || exit 1

# JVM options for better performance
ENV JAVA_OPTS="-Xms512m -Xmx2g -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+UseStringDeduplication"

# Start application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -Djava.security.egd=file:/dev/./urandom -jar app.jar"]
