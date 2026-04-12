"""
Viral Content Discovery System for Pure Technology

Discovers trending/viral content across social platforms:
- LinkedIn: Professional thought leadership
- Twitter/X: Real-time trends and hot takes
- Reddit: Community discussions
- TikTok: Viral brand content
- Instagram: Brand activations
- Google Trends: Rising search topics

Enables:
- Reposting relevant content
- Piggybacking on trends
- Riding viral waves
- Early engagement opportunities
"""

from .viral_discovery import ViralContentDiscovery
from .viral_digest import generate_daily_digest

__all__ = ["ViralContentDiscovery", "generate_daily_digest"]
