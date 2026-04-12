"""
Experiential Intent Engine
Automated CPG prospect signal collection, scoring, and daily action queue

Components:
- airtable_client: CRUD operations for Airtable
- openai_classifier: Intent signal classification
- apify_collector: LinkedIn signal collection
- twitter_collector: Twitter/X signal collection
- email_dashboard: Daily email reports
- prospect_discovery: Auto-discover prospects matching ICPs
- icp_config: ICP configuration management
- main: Orchestrator
"""

from .config import *
from .airtable_client import (
    get_all_people,
    get_people_with_linkedin,
    get_ready_prospects,
    get_warm_prospects,
    create_signal,
    create_person,
    find_person_by_linkedin,
    get_recent_signals,
    count_by_status,
    update_person_last_checked,
    update_company,
)
from .openai_classifier import (
    classify_linkedin_activity,
    classify_simple_signal,
)
from .apify_collector import (
    collect_signals,
    parse_profile_for_signals,
    list_tasks,
)
from .twitter_collector import (
    collect_twitter_signals,
    parse_twitter_signals,
)
from .email_dashboard import (
    generate_dashboard_html,
    send_dashboard_email,
    preview_dashboard,
)
from .icp_config import (
    load_icp_config,
    list_icps,
    get_icp_display_name,
)
from .prospect_discovery import (
    discover_prospects,
    discover_all_icps,
    score_prospect,
    filter_by_icp,
    learn_from_feedback,
)

__version__ = "0.1.0"
