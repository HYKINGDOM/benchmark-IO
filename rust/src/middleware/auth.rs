use actix_web::{dev::Payload, error, Error, FromRequest, HttpRequest};
use futures::future::{ready, Ready};
use std::sync::Arc;

use crate::config::Config;

/// API Key 认证中间件
pub struct ApiKeyAuth {
    pub is_authenticated: bool,
}

impl ApiKeyAuth {
    pub fn new(is_authenticated: bool) -> Self {
        Self { is_authenticated }
    }
}

impl FromRequest for ApiKeyAuth {
    type Error = Error;
    type Future = Ready<Result<Self, Self::Error>>;

    fn from_request(req: &HttpRequest, _: &mut Payload) -> Self::Future {
        let config = req.app_data::<Arc<Config>>()
            .expect("Config not found in app data");

        // 从 Header 获取 API Key
        let api_key = req.headers()
            .get("X-API-Key")
            .and_then(|v| v.to_str().ok());

        match api_key {
            Some(key) if key == config.api_key => {
                ready(Ok(ApiKeyAuth::new(true)))
            }
            _ => {
                ready(Err(error::ErrorUnauthorized(
                    serde_json::json!({
                        "error": "Unauthorized",
                        "message": "Invalid or missing API key"
                    })
                )))
            }
        }
    }
}

/// 可选的 API Key 认证（用于某些公开接口）
pub struct OptionalApiKeyAuth {
    pub is_authenticated: bool,
}

impl FromRequest for OptionalApiKeyAuth {
    type Error = Error;
    type Future = Ready<Result<Self, Self::Error>>;

    fn from_request(req: &HttpRequest, _: &mut Payload) -> Self::Future {
        let config = req.app_data::<Arc<Config>>()
            .expect("Config not found in app data");

        let api_key = req.headers()
            .get("X-API-Key")
            .and_then(|v| v.to_str().ok());

        let is_authenticated = api_key
            .map(|key| key == config.api_key)
            .unwrap_or(false);

        ready(Ok(OptionalApiKeyAuth { is_authenticated }))
    }
}
