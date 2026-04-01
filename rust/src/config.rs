use std::env;

#[derive(Debug, Clone)]
pub struct Config {
    pub database_url: String,
    pub server_host: String,
    pub server_port: u16,
    pub api_key: String,
    pub export_dir: String,
}

impl Config {
    pub fn from_env() -> Self {
        dotenv::dotenv().ok();
        
        Self {
            database_url: env::var("DATABASE_URL")
                .expect("DATABASE_URL must be set"),
            server_host: env::var("SERVER_HOST")
                .unwrap_or_else(|_| "0.0.0.0".to_string()),
            server_port: env::var("SERVER_PORT")
                .unwrap_or_else(|_| "8080".to_string())
                .parse()
                .expect("SERVER_PORT must be a valid port number"),
            api_key: env::var("API_KEY")
                .expect("API_KEY must be set"),
            export_dir: env::var("EXPORT_DIR")
                .unwrap_or_else(|_| "./exports".to_string()),
        }
    }
}
