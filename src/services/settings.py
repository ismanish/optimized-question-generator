"""
Application settings and configuration.
"""
import os
from typing import Dict, Any

# Environment constants
DEV = "development"
STAGING = "staging"
PROD = "production"

# Get environment or default to development
ENV = os.environ.get("APP_ENV", DEV)

# Base configurations
BASE_CONFIG: Dict[str, Any] = {
    "app_name": "Question Generation API",
    "version": "1.0.0",
    "debug": False,
    "aws_region": os.environ.get("AWS_REGION", "us-east-1"),
    "dynamodb_table": "question_generation_history",
}

# Environment-specific configurations
ENV_CONFIGS: Dict[str, Dict[str, Any]] = {
    DEV: {
        "debug": True,
    },
    STAGING: {
        "debug": False,
    },
    PROD: {
        "debug": False,
    }
}

# Merge base config with environment-specific config
def get_settings() -> Dict[str, Any]:
    """
    Get application settings based on current environment.
    
    Returns:
        Dict containing merged configuration settings
    """
    config = BASE_CONFIG.copy()
    config.update(ENV_CONFIGS.get(ENV, {}))
    return config