"""
Experiential Intent Engine Configuration
Load from .env file
"""
import os
from pathlib import Path

# Find .env file
ENV_PATH = Path(__file__).parent.parent.parent / ".env"

def load_env():
    """Load environment variables from .env file"""
    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()

# API Keys
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APIFY_API_KEY = os.getenv("APIFY_API_KEY")

# Airtable Table IDs
PEOPLE_TABLE = "tblzttcsprjQFWBmt"
SIGNALS_TABLE = "tbl7w57ZbGh2Z7BkE"
COMPANIES_TABLE = "tblOlRcyiCGrZbFDx"

# Airtable Field IDs - People
PEOPLE_FIELDS = {
    "name": "fldsKhXv5GAr4Xu8x",
    "linkedin_url": "fldrTikuYF69C3YOy",
    "twitter_handle": "fldTwitterHandle",  # Twitter handle (@username)
    "twitter_url": "fldTwitterUrl",  # Twitter URL (twitter.com/user or x.com/user)
    "title": "fldKFAWo5Sdo83P7d",
    "company_link": "fldFetiIlqGCL5hqJ",
    "seniority": "flddZwoFvti1DZjKg",
    "function_type": "fldtpKCiPgGWO8AQS",
    "signals": "fld3NhNzMBzeyFyzz",
    "rolling_intent_score": "fld243TU1PVaP1hGa",
    "readiness_flag": "fldeax1jrHPGSi02H",
}

# Airtable Field IDs - Signals
SIGNALS_FIELDS = {
    "signal_type": "fldVKlz7ECv4PkVxi",
    "signal_strength": "fld0lX4uPeznrtW36",
    "source": "fldhZds8meNYhyXfh",
    "signal_timestamp": "fldsomMOtxnOaaEZ1",
    "signal_category": "fldXNfapYU4cJCD0p",
    "person_link": "fld7c6fR2e6gKrAaW",
    "linkedin_url": "fld9wadQnKvrgINU4",
}

# Signal Type Options (must match Airtable dropdown exactly)
SIGNAL_TYPES = [
    "liked_experiential_post",
    "commented_on_activation",
    "posted_about_launch",
    "follows_experiential_page",
    "commented_on_competitor",
    "timing_trigger",
]

# Source Options
SOURCES = ["LinkedIn", "Twitter", "Google Alert", "Crunchbase", "RSS", "Manual"]

# Email Config
EMAIL_RECIPIENT = "purebrain@puremarketing.ai"

# Twitter/X Collection (via Apify)
# Uses Apify Twitter scrapers instead of official Twitter API
# Set APIFY_API_KEY in .env file (same key used for LinkedIn)
# The Twitter API keys below are deprecated but kept for reference
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")  # DEPRECATED - use Apify
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")  # DEPRECATED - use Apify
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")  # DEPRECATED - use Apify
