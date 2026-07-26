"""
Distribution Engine — Configuration Loader

Loads distribution_config.json and merges with environment variables.
Environment variables always override file-based config.
"""

import os
import json


_CONFIG_FILENAME = "distribution_config.json"


def load_config() -> dict:
    """
    Load the distribution configuration.

    Searches for distribution_config.json relative to this file's location,
    then applies environment variable overrides.

    Returns:
        Merged configuration dict.
    """
    # Look for config relative to the _automation directory
    automation_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(automation_dir, _CONFIG_FILENAME)

    if not os.path.exists(config_path):
        print(f"  ⚠️ Distribution config not found at {config_path}. Using defaults.")
        return _default_config()

    with open(config_path, "r") as f:
        config = json.load(f)

    # Environment variable overrides (booleans)
    _env_bool_override(config, "enable_push", "DIST_ENABLE_PUSH")
    _env_bool_override(config, "enable_newsletter", "DIST_ENABLE_NEWSLETTER")
    _env_bool_override(config, "enable_digest", "DIST_ENABLE_DIGEST")
    _env_bool_override(config, "enable_rss_validation", "DIST_ENABLE_RSS")
    _env_bool_override(config, "enable_email_verification", "DIST_ENABLE_VERIFICATION")
    _env_bool_override(config, "enable_email", "DIST_ENABLE_EMAIL")
    _env_bool_override(config, "enable_website_notifications", "DIST_ENABLE_WEBSITE_NOTIFICATIONS")

    # Environment variable overrides (strings)
    _env_str_override(config, "site_url", "DIST_SITE_URL")
    _env_str_override(config, "digest_time", "DIST_DIGEST_TIME")

    # SMTP config from environment (secrets)
    config["smtp"] = config.get("smtp", {})
    config["smtp"]["host"] = os.environ.get("SMTP_HOST", config["smtp"].get("host", "smtp.gmail.com"))
    config["smtp"]["port"] = int(os.environ.get("SMTP_PORT", config["smtp"].get("port", 587)))
    config["smtp"]["email"] = os.environ.get("SMTP_EMAIL", config["smtp"].get("email", ""))
    config["smtp"]["password"] = os.environ.get("SMTP_PASSWORD", config["smtp"].get("password", ""))
    config["smtp"]["use_tls"] = config["smtp"].get("use_tls", True)

    # Firebase config from environment
    config["firebase_service_account"] = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "")
    config["fcm_vapid_key"] = os.environ.get("FCM_VAPID_KEY", "")

    # Optional Email Provider setup
    config["email_provider"] = _init_email_provider(config)

    return config

def _init_email_provider(config: dict):
    """
    Instantiate the appropriate EmailProvider if configured.
    Returns None if no email provider is configured or enabled.
    """
    if not config.get("enable_email", False):
        return None

    provider_type = config.get("email_provider_type", "smtp").lower()

    if provider_type == "smtp":
        if not config["smtp"].get("email") or not config["smtp"].get("password"):
            print("  ⚠️ SMTP enabled but credentials missing. Email delivery disabled.")
            return None

        try:
            from distribution.providers.smtp_provider import SMTPEmailProvider
            return SMTPEmailProvider({
                "smtp_host": config["smtp"]["host"],
                "smtp_port": config["smtp"]["port"],
                "smtp_email": config["smtp"]["email"],
                "smtp_password": config["smtp"]["password"],
                "smtp_use_tls": config["smtp"]["use_tls"],
            })
        except Exception as e:
            print(f"  ❌ Failed to initialize SMTP provider: {e}")
            return None

    print(f"  ⚠️ Unknown email provider type: {provider_type}")
    return None

def _env_bool_override(config: dict, key: str, env_var: str):
    """Override a config boolean with an environment variable."""
    val = os.environ.get(env_var)
    if val is not None:
        config[key] = val.lower() in ("true", "1", "yes")


def _env_str_override(config: dict, key: str, env_var: str):
    """Override a config string with an environment variable."""
    val = os.environ.get(env_var)
    if val is not None:
        config[key] = val


def _default_config() -> dict:
    """Return sensible defaults if no config file exists."""
    return {
        "enable_push": False,
        "enable_newsletter": False,
        "enable_digest": False,
        "enable_rss_validation": True,
        "enable_email_verification": True,
        "enable_email": False,
        "enable_website_notifications": True,
        "email_provider_type": "smtp",
        "digest_time": "08:00",
        "digest_timezone": "Asia/Kolkata",
        "max_notifications_per_run": 500,
        "site_url": "https://mantbyte.github.io",
        "site_name": "Mantbyte",
        "from_email": "noreply@mantbyte.github.io",
        "newsletter_categories": ["Tech", "News", "Geopolitics"],
        "push_notification": {
            "title_prefix": "🚀 New Mantbyte Article",
            "icon": "/assets/images/favicon.svg",
            "badge": "/assets/images/favicon.svg",
        },
        "digest": {
            "subject_prefix": "Mantbyte Daily Digest",
            "max_articles": 10,
        },
        "smtp": {
            "host": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            "email": "",
            "password": "",
        },
        "firebase_service_account": "",
        "fcm_vapid_key": "",
    }
