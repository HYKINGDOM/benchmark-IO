package com.benchmark.config;

import com.zaxxer.hikari.HikariDataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import javax.sql.DataSource;

/**
 * Database Configuration
 *
 * @author Benchmark Team
 */
@Configuration
public class DatabaseConfig {

    @Value("${spring.datasource.url}")
    private String datasourceUrl;

    @Value("${spring.datasource.username}")
    private String datasourceUsername;

    @Value("${spring.datasource.password}")
    private String datasourcePassword;

    @Value("${spring.datasource.hikari.maximum-pool-size:50}")
    private int maximumPoolSize;

    @Value("${spring.datasource.hikari.minimum-idle:10}")
    private int minimumIdle;

    /**
     * Configure HikariCP DataSource
     */
    @Bean
    public DataSource dataSource() {
        HikariDataSource dataSource = new HikariDataSource();
        dataSource.setJdbcUrl(datasourceUrl);
        dataSource.setUsername(datasourceUsername);
        dataSource.setPassword(datasourcePassword);
        dataSource.setMaximumPoolSize(maximumPoolSize);
        dataSource.setMinimumIdle(minimumIdle);
        dataSource.setPoolName("BenchmarkHikariPool");
        dataSource.setIdleTimeout(300000);
        dataSource.setMaxLifetime(1800000);
        dataSource.setConnectionTimeout(30000);
        dataSource.setLeakDetectionThreshold(60000);

        // PostgreSQL optimizations
        dataSource.addDataSourceProperty("preparedStatementCacheQueries", 256);
        dataSource.addDataSourceProperty("preparedStatementCacheSizeMiB", 5);
        dataSource.addDataSourceProperty("reWriteBatchedInserts", true);

        return dataSource;
    }

    /**
     * Configure JOOQ DSLContext
     */
    @Bean
    public DSLContext dslContext(DataSource dataSource) {
        return DSL.using(dataSource, SQLDialect.POSTGRES);
    }
}
