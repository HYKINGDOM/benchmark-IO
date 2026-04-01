use diesel::pg::PgConnection;
use diesel::r2d2::{self, ConnectionManager};
use std::env;

pub type DbPool = r2d2::Pool<ConnectionManager<PgConnection>>;
pub type DbConnection = r2d2::PooledConnection<ConnectionManager<PgConnection>>;

/// 创建数据库连接池
pub fn create_pool() -> DbPool {
    let database_url = env::var("DATABASE_URL")
        .expect("DATABASE_URL must be set");
    
    let manager = ConnectionManager::<PgConnection>::new(database_url);
    
    r2d2::Pool::builder()
        .max_size(10)
        .build(manager)
        .expect("Failed to create pool.")
}

/// 获取数据库连接
pub fn get_connection(pool: &DbPool) -> Result<DbConnection, String> {
    pool.get()
        .map_err(|e| format!("Failed to get database connection: {}", e))
}
