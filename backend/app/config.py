"""Configuration management for the mail service."""

from typing import List, Optional

from pydantic_settings import BaseSettings


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

    # Enhanced Logging Configuration
    log_format: str = "json"  # json, text
    log_file_enabled: bool = False
    log_file_path: str = "./logs/app.log"
    log_max_files: int = 5
    log_max_size: str = "10m"
    log_include_request_id: bool = True
    log_include_user_info: bool = True
    log_include_sensitive_data: bool = False  # Set to True for debugging
    log_performance_metrics: bool = True
    log_smtp_details: bool = False  # Set to True for SMTP debugging
    log_email_content: bool = False  # Set to True to log email content (be careful with sensitive data)
    log_correlation_id: bool = True
    log_request_response: bool = False  # Set to True to log full request/response
    log_slow_requests_threshold: float = 1.0  # Log requests slower than this (seconds)

    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 30

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
