#!/usr/bin/env python3
"""Script to check if required services are running and accessible."""

import asyncio
import sys
import os
import aiosmtplib
import httpx
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.config import settings


async def check_kube_mail_connection() -> Dict[str, Any]:
    """Check if kube-mail service is accessible."""
    try:
        smtp = aiosmtplib.SMTP(hostname=settings.kube_mail_host, port=settings.kube_mail_port)
        await smtp.connect()
        await smtp.quit()
        return {
            "status": "healthy",
            "message": f"Successfully connected to {settings.kube_mail_host}:{settings.kube_mail_port}"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Failed to connect to {settings.kube_mail_host}:{settings.kube_mail_port}: {str(e)}"
        }


async def check_backend_service() -> Dict[str, Any]:
    """Check if the backend service is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/health", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "message": f"Backend service is running. Status: {data.get('status', 'unknown')}"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Backend service returned status code: {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Backend service is not accessible: {str(e)}"
        }


async def check_frontend_service() -> Dict[str, Any]:
    """Check if the frontend service is running."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:3000/health", timeout=5.0)
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "message": "Frontend service is running"
                }
            else:
                return {
                    "status": "unhealthy",
                    "message": f"Frontend service returned status code: {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Frontend service is not accessible: {str(e)}"
        }


async def main():
    """Main function to check all services."""
    print("🔍 Checking Mail Service Dependencies...")
    print("=" * 50)
    
    # Check kube-mail connection
    print("📧 Checking kube-mail connection...")
    kube_mail_result = await check_kube_mail_connection()
    print(f"   Status: {kube_mail_result['status'].upper()}")
    print(f"   Message: {kube_mail_result['message']}")
    print()
    
    # Check backend service
    print("🔧 Checking backend service...")
    backend_result = await check_backend_service()
    print(f"   Status: {backend_result['status'].upper()}")
    print(f"   Message: {backend_result['message']}")
    print()
    
    # Check frontend service
    print("🎨 Checking frontend service...")
    frontend_result = await check_frontend_service()
    print(f"   Status: {frontend_result['status'].upper()}")
    print(f"   Message: {frontend_result['message']}")
    print()
    
    # Summary
    print("📊 Summary:")
    print("=" * 50)
    
    all_healthy = all([
        kube_mail_result['status'] == 'healthy',
        backend_result['status'] == 'healthy',
        frontend_result['status'] == 'healthy'
    ])
    
    if all_healthy:
        print("✅ All services are healthy and ready!")
        return 0
    else:
        print("❌ Some services are not healthy. Please check the configuration.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
