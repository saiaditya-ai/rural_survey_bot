import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from models.database import Base

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/ruralbot")

# Convert to async URL if needed
if DATABASE_URL.startswith("postgresql://"):
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DEBUG", "False").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

async def check_db_connection():
    """Check database connection health"""
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute(text("SELECT 1"))
            await result.fetchone()
            
        return {
            "status": "healthy",
            "message": "Database connection successful",
            "response_time_ms": 0  # You could measure this
        }
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
            "error": str(e)
        }

async def test_database_operations():
    """Test basic database operations"""
    test_results = []
    
    try:
        async with AsyncSessionLocal() as session:
            # Test 1: Basic connection
            try:
                await session.execute(text("SELECT 1"))
                test_results.append({
                    "test": "connection",
                    "status": "pass",
                    "message": "Database connection successful"
                })
            except Exception as e:
                test_results.append({
                    "test": "connection",
                    "status": "fail",
                    "message": f"Connection failed: {str(e)}"
                })
            
            # Test 2: Table existence
            try:
                tables_to_check = ["surveys", "chat_sessions", "chat_messages"]
                for table in tables_to_check:
                    result = await session.execute(
                        text(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table}'")
                    )
                    count = (await result.fetchone())[0]
                    if count > 0:
                        test_results.append({
                            "test": f"table_{table}",
                            "status": "pass",
                            "message": f"Table {table} exists"
                        })
                    else:
                        test_results.append({
                            "test": f"table_{table}",
                            "status": "fail",
                            "message": f"Table {table} does not exist"
                        })
            except Exception as e:
                test_results.append({
                    "test": "table_check",
                    "status": "fail",
                    "message": f"Table check failed: {str(e)}"
                })
            
            # Test 3: Insert/Select operation
            try:
                # Try to count records in surveys table
                result = await session.execute(text("SELECT COUNT(*) FROM surveys"))
                count = (await result.fetchone())[0]
                test_results.append({
                    "test": "select_operation",
                    "status": "pass",
                    "message": f"Select operation successful. Found {count} surveys."
                })
            except Exception as e:
                test_results.append({
                    "test": "select_operation",
                    "status": "fail",
                    "message": f"Select operation failed: {str(e)}"
                })
                
    except Exception as e:
        test_results.append({
            "test": "overall",
            "status": "fail",
            "message": f"Database test failed: {str(e)}"
        })
    
    return test_results

async def get_database_stats():
    """Get database statistics"""
    try:
        async with AsyncSessionLocal() as session:
            stats = {}
            
            # Get table counts
            tables = ["surveys", "chat_sessions", "chat_messages", "api_usage", "scraping_logs"]
            for table in tables:
                try:
                    result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = (await result.fetchone())[0]
                    stats[f"{table}_count"] = count
                except Exception as e:
                    stats[f"{table}_count"] = f"Error: {str(e)}"
            
            # Get recent activity
            try:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM surveys WHERE timestamp > NOW() - INTERVAL '24 hours'")
                )
                stats["surveys_last_24h"] = (await result.fetchone())[0]
            except Exception as e:
                stats["surveys_last_24h"] = f"Error: {str(e)}"
            
            try:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM chat_messages WHERE timestamp > NOW() - INTERVAL '24 hours'")
                )
                stats["messages_last_24h"] = (await result.fetchone())[0]
            except Exception as e:
                stats["messages_last_24h"] = f"Error: {str(e)}"
            
            return stats
            
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        return {"error": str(e)}

class DatabaseManager:
    """Database manager for common operations"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def execute_query(self, query: str, params: dict = None):
        """Execute a raw SQL query"""
        async with self.session_factory() as session:
            result = await session.execute(text(query), params or {})
            return await result.fetchall()
    
    async def get_table_info(self, table_name: str):
        """Get information about a table"""
        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = :table_name
        ORDER BY ordinal_position
        """
        return await self.execute_query(query, {"table_name": table_name})
    
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old data"""
        cleanup_results = []
        
        try:
            async with self.session_factory() as session:
                # Clean up old chat sessions
                result = await session.execute(
                    text(f"DELETE FROM chat_sessions WHERE last_activity < NOW() - INTERVAL '{days} days'")
                )
                cleanup_results.append({
                    "table": "chat_sessions",
                    "deleted_rows": result.rowcount
                })
                
                # Clean up old API usage logs
                result = await session.execute(
                    text(f"DELETE FROM api_usage WHERE timestamp < NOW() - INTERVAL '{days} days'")
                )
                cleanup_results.append({
                    "table": "api_usage",
                    "deleted_rows": result.rowcount
                })
                
                # Clean up old scraping logs
                result = await session.execute(
                    text(f"DELETE FROM scraping_logs WHERE timestamp < NOW() - INTERVAL '{days} days'")
                )
                cleanup_results.append({
                    "table": "scraping_logs",
                    "deleted_rows": result.rowcount
                })
                
                # Clean up expired cache entries
                result = await session.execute(
                    text("DELETE FROM cache_entries WHERE expires_at < NOW()")
                )
                cleanup_results.append({
                    "table": "cache_entries",
                    "deleted_rows": result.rowcount
                })
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            cleanup_results.append({
                "error": str(e)
            })
        
        return cleanup_results
    
    async def backup_data(self, table_name: str, output_file: str):
        """Backup table data to JSON file"""
        try:
            import json
            from datetime import datetime
            
            async with self.session_factory() as session:
                result = await session.execute(text(f"SELECT * FROM {table_name}"))
                rows = await result.fetchall()
                
                # Convert to list of dictionaries
                data = []
                for row in rows:
                    row_dict = {}
                    for key, value in row._mapping.items():
                        if isinstance(value, datetime):
                            row_dict[key] = value.isoformat()
                        else:
                            row_dict[key] = value
                    data.append(row_dict)
                
                # Write to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "table": table_name,
                        "backup_date": datetime.utcnow().isoformat(),
                        "record_count": len(data),
                        "data": data
                    }, f, indent=2, ensure_ascii=False)
                
                return {
                    "success": True,
                    "table": table_name,
                    "records_backed_up": len(data),
                    "output_file": output_file
                }
                
        except Exception as e:
            logger.error(f"Error backing up data: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
