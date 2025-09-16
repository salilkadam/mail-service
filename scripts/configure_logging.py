#!/usr/bin/env python3
"""Script to configure logging settings dynamically for the mail service."""

import argparse
import json
import os
import sys
from typing import Dict, Any

# Add the backend directory to the path so we can import the config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.config import settings


def get_current_logging_config() -> Dict[str, Any]:
    """Get current logging configuration."""
    return {
        "log_level": settings.log_level,
        "log_format": settings.log_format,
        "log_file_enabled": settings.log_file_enabled,
        "log_file_path": settings.log_file_path,
        "log_include_request_id": settings.log_include_request_id,
        "log_include_user_info": settings.log_include_user_info,
        "log_include_sensitive_data": settings.log_include_sensitive_data,
        "log_performance_metrics": settings.log_performance_metrics,
        "log_smtp_details": settings.log_smtp_details,
        "log_email_content": settings.log_email_content,
        "log_correlation_id": settings.log_correlation_id,
        "log_request_response": settings.log_request_response,
        "log_slow_requests_threshold": settings.log_slow_requests_threshold,
    }


def print_current_config():
    """Print current logging configuration."""
    config = get_current_logging_config()
    print("Current Logging Configuration:")
    print("=" * 50)
    for key, value in config.items():
        print(f"{key}: {value}")
    print()


def print_environment_variables():
    """Print environment variables for logging configuration."""
    print("Environment Variables for Logging Configuration:")
    print("=" * 60)
    
    env_vars = [
        "LOG_LEVEL",
        "LOG_FORMAT", 
        "LOG_FILE_ENABLED",
        "LOG_FILE_PATH",
        "LOG_INCLUDE_REQUEST_ID",
        "LOG_INCLUDE_USER_INFO",
        "LOG_INCLUDE_SENSITIVE_DATA",
        "LOG_PERFORMANCE_METRICS",
        "LOG_SMTP_DETAILS",
        "LOG_EMAIL_CONTENT",
        "LOG_CORRELATION_ID",
        "LOG_REQUEST_RESPONSE",
        "LOG_SLOW_REQUESTS_THRESHOLD",
    ]
    
    for var in env_vars:
        value = os.getenv(var, "Not set")
        print(f"{var}: {value}")
    print()


def generate_kubectl_patch():
    """Generate kubectl patch command for updating logging configuration."""
    print("Kubectl Patch Commands for Production:")
    print("=" * 50)
    
    # High verbosity configuration for debugging
    high_verbosity = {
        "LOG_LEVEL": "DEBUG",
        "LOG_SMTP_DETAILS": "true",
        "LOG_EMAIL_CONTENT": "true",
        "LOG_REQUEST_RESPONSE": "true",
        "LOG_INCLUDE_SENSITIVE_DATA": "true",
    }
    
    print("# High verbosity logging (for debugging):")
    print("kubectl patch configmap mail-service-config -n mail-service-prod --type merge -p '{\"data\":{")
    for i, (key, value) in enumerate(high_verbosity.items()):
        comma = "," if i < len(high_verbosity) - 1 else ""
        print(f'    "{key}": "{value}"{comma}')
    print("}}'")
    print()
    
    # Normal production configuration
    normal_config = {
        "LOG_LEVEL": "INFO",
        "LOG_SMTP_DETAILS": "false",
        "LOG_EMAIL_CONTENT": "false",
        "LOG_REQUEST_RESPONSE": "false",
        "LOG_INCLUDE_SENSITIVE_DATA": "false",
    }
    
    print("# Normal production logging:")
    print("kubectl patch configmap mail-service-config -n mail-service-prod --type merge -p '{\"data\":{")
    for i, (key, value) in enumerate(normal_config.items()):
        comma = "," if i < len(normal_config) - 1 else ""
        print(f'    "{key}": "{value}"{comma}')
    print("}}'")
    print()
    
    # Restart deployment to apply changes
    print("# Restart deployment to apply configuration changes:")
    print("kubectl rollout restart deployment/backend-deployment -n mail-service-prod")
    print()


def generate_docker_compose_env():
    """Generate environment variables for docker-compose."""
    print("Docker Compose Environment Variables:")
    print("=" * 40)
    
    # Debug configuration
    debug_config = {
        "LOG_LEVEL": "DEBUG",
        "LOG_SMTP_DETAILS": "true",
        "LOG_EMAIL_CONTENT": "true",
        "LOG_REQUEST_RESPONSE": "true",
        "LOG_INCLUDE_SENSITIVE_DATA": "true",
    }
    
    print("# Add these to your docker-compose.yml environment section for debugging:")
    for key, value in debug_config.items():
        print(f"      - {key}={value}")
    print()


def show_logging_presets():
    """Show different logging presets."""
    print("Logging Configuration Presets:")
    print("=" * 40)
    
    presets = {
        "production": {
            "description": "Standard production logging",
            "config": {
                "LOG_LEVEL": "INFO",
                "LOG_FORMAT": "json",
                "LOG_SMTP_DETAILS": "false",
                "LOG_EMAIL_CONTENT": "false",
                "LOG_REQUEST_RESPONSE": "false",
                "LOG_INCLUDE_SENSITIVE_DATA": "false",
            }
        },
        "debug": {
            "description": "High verbosity for debugging issues",
            "config": {
                "LOG_LEVEL": "DEBUG",
                "LOG_FORMAT": "json",
                "LOG_SMTP_DETAILS": "true",
                "LOG_EMAIL_CONTENT": "true",
                "LOG_REQUEST_RESPONSE": "true",
                "LOG_INCLUDE_SENSITIVE_DATA": "true",
            }
        },
        "performance": {
            "description": "Performance monitoring with minimal overhead",
            "config": {
                "LOG_LEVEL": "INFO",
                "LOG_FORMAT": "json",
                "LOG_PERFORMANCE_METRICS": "true",
                "LOG_SLOW_REQUESTS_THRESHOLD": "0.5",
                "LOG_SMTP_DETAILS": "false",
                "LOG_EMAIL_CONTENT": "false",
            }
        },
        "security": {
            "description": "Security-focused logging (no sensitive data)",
            "config": {
                "LOG_LEVEL": "INFO",
                "LOG_FORMAT": "json",
                "LOG_INCLUDE_SENSITIVE_DATA": "false",
                "LOG_EMAIL_CONTENT": "false",
                "LOG_REQUEST_RESPONSE": "false",
                "LOG_SMTP_DETAILS": "false",
            }
        }
    }
    
    for preset_name, preset_data in presets.items():
        print(f"\n{preset_name.upper()}:")
        print(f"  Description: {preset_data['description']}")
        print("  Configuration:")
        for key, value in preset_data['config'].items():
            print(f"    {key}: {value}")
    print()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Configure logging for mail service")
    parser.add_argument("--current", action="store_true", help="Show current configuration")
    parser.add_argument("--env", action="store_true", help="Show environment variables")
    parser.add_argument("--kubectl", action="store_true", help="Generate kubectl patch commands")
    parser.add_argument("--docker", action="store_true", help="Generate docker-compose environment")
    parser.add_argument("--presets", action="store_true", help="Show logging presets")
    parser.add_argument("--all", action="store_true", help="Show all information")
    
    args = parser.parse_args()
    
    if args.all or not any([args.current, args.env, args.kubectl, args.docker, args.presets]):
        # Show all by default
        print_current_config()
        print_environment_variables()
        show_logging_presets()
        generate_kubectl_patch()
        generate_docker_compose_env()
    else:
        if args.current:
            print_current_config()
        if args.env:
            print_environment_variables()
        if args.presets:
            show_logging_presets()
        if args.kubectl:
            generate_kubectl_patch()
        if args.docker:
            generate_docker_compose_env()


if __name__ == "__main__":
    main()
