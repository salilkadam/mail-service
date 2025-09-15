"""Configuration management for the mail service."""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Mail Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    use_tls: bool = True
    from_email: str = "info@bionicaisolutions.com"
    from_name: str = "Bionic AI Solutions"
    
    # Application Configuration
    app_name: str = "Mail Service"
    app_version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
