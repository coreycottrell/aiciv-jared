"""PureSurf Social Schedule v2 — BaaS Single Source of Truth
Enhanced schedule API endpoints with:
  - Extended fields (baas_id, drive_folder_url, drive_file_ids, etc.)
  - New endpoints (approve, publish, sync-status, sync-sheets, calendar, bulk, stats)
  - Auto-sync to Google Sheets on every write

Replaces the inline /social/schedule endpoints in baas_server_simple.py.

Author: dept-systems-technology
Date: 2026-04-06
"""

import asyncio
import json
import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field

log = logging.getLogger('baas.schedule')

# ==================== CONFIGURATION ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEDULED_POSTS_FILE = os.path.join(BASE_DIR, 'scheduled_posts.json')

# ==================== MODELS ====================

VALID_CONTENT_TYPES = ['blog', 'standalone', 'newsletter', 'bluesky_thread', 'linkedin', 'social_post']
VALID_STATUSES = ['draft', 'approved', 'scheduled', 'publishing', 'posted', 'failed']


class ScheduleCreateReq(BaseModel):
    """Create a new schedule entry."""
    platform: str = 'linkedin'
    content: str = ''
    title: str = ''
    content_type: str = 'standalone'
    scheduled_time: Optional[str] = None
    media_path: Optional[str] = None
    banner_image: str = ''
    banner_url: str = ''
    blog_url: str = ''
    linkedin_post_url: str = ''
    newsletter_status: str = ''
    audio_status: str = ''
    drive_folder_url: str = ''
    drive_file_ids: Dict[str, str] = {}
    status: str = 'draft'
    auto_publish: bool = False


class ScheduleUpdateReq(BaseModel):
    """Update an existing schedule entry."""
    platform: Optional[str] = None
    content: Optional[str] = None
    title: Optional[str] = None
    content_type: Optional[str] = None
    scheduled_time: Optional[str] = None
    media_path: Optional[str] = None
    banner_image: Optional[str] = None
    banner_url: Optional[str] = None
    blog_url: Optional[str] = None
    linkedin_post_url: Optional[str] = None
    newsletter_status: Optional[str] = None
    audio_status: Optional[str] = None
    drive_folder_url: Optional[str] = None
    drive_file_ids: Optional[Dict[str, str]] = None
    status: Optional[str] = None
    auto_publish: Optional[bool] = None


class BulkScheduleReq(BaseModel):
    """Create multiple schedule entries at once."""
    entries: List[ScheduleCreateReq]


# ==================== PERSISTENCE ====================

_sync_callback = None  # Set by extend_schedule_router to trigger sheet sync


def _load_scheduled() -> Dict[str, dict]:
    try:
        with open(SCHEDULED_POSTS_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def _save_scheduled(data: Dict[str, dict]):
    with open(SCHEDULED_POSTS_FILE, 'w') as f:
        json.dump(data, f, indent=2, default=str)


def _make_baas_id() -> str:
    """Generate a unique baas_id."""
    return f"post-{int(time.time())}-{uuid.uuid4().hex[:6]}"


def _enrich_post(body: dict, post_id: str = None) -> dict:
    """Ensure all v2 fields exist on a post record."""
    now = datetime.now(timezone.utc).isoformat()
    baas_id = post_id or body.get('id') or _make_baas_id()

    defaults = {
        'id': baas_id,
        'baas_id': baas_id,
        'platform': 'linkedin',
        'content': '',
        'title': '',
        'content_type': 'standalone',
        'scheduled_time': None,
        'media_path': None,
        'banner_image': '',
        'banner_url': '',
        'blog_url': '',
        'linkedin_post_url': '',
        'newsletter_status': '',
        'audio_status': '',
        'drive_folder_url': '',
        'drive_file_ids': {},
        'spreadsheet_row': None,
        'publish_status': 'draft',
        'status': 'draft',
        'auto_publish': False,
        'created_at': now,
        'updated_at': now,
    }

    # Merge: defaults <- existing <- new body
    result = {**defaults}
    for k, v in body.items():
        if v is not None:
            result[k] = v

    # Ensure baas_id matches id
    result['baas_id'] = result['id']
    # Ensure publish_status mirrors status
    result['publish_status'] = result.get('status', 'draft')
    result['updated_at'] = now

    return result


async def _trigger_sync(post: dict, action: str = 'upsert'):
    """Call the sheet sync callback if registered."""
    if _sync_callback:
        try:
            await _sync_callback(post, action)
        except Exception as e:
            log.error(f'Sheet sync failed for {post.get("id")}: {e}')


# ==================== ROUTER FACTORY ====================

def create_schedule_router(sessions_ref: dict, auth_fn):
    """Create the v2 schedule router with all enhanced endpoints."""

    router = APIRouter(prefix='/social/schedule', tags=['Schedule v2'])

    # ── POST /social/schedule — Create ──
    @router.post('')
    async def create_schedule_entry(request: Request, x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        body = await request.json()
        posts = _load_scheduled()

        post_id = body.get('id') or _make_baas_id()
        post = _enrich_post(body, post_id)
        posts[post_id] = post
        _save_scheduled(posts)

        log.info(f'Schedule created: {post_id} [{post["platform"]}] [{post["content_type"]}]')
        await _trigger_sync(post, 'upsert')
        return {'ok': True, 'post': post}

    # ── GET /social/schedule — List all (with filters) ──
    @router.get('')
    async def list_schedule_entries(
        status: Optional[str] = None,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        x_api_key: str = Header(None),
    ):
        auth_fn(x_api_key)
        posts = list(_load_scheduled().values())

        if status:
            posts = [p for p in posts if p.get('status') == status]
        if platform:
            posts = [p for p in posts if p.get('platform') == platform]
        if content_type:
            posts = [p for p in posts if p.get('content_type') == content_type]

        # Sort by scheduled_time
        posts.sort(key=lambda p: p.get('scheduled_time') or '', reverse=True)
        return {'posts': posts, 'count': len(posts)}

    # ── FIXED: Specific routes BEFORE parameterized routes ──

    # ── GET /social/schedule/sync-status — Sync health ──
    @router.get('/sync-status')
    async def sync_status(x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        posts = _load_scheduled()
        synced = sum(1 for p in posts.values() if p.get('spreadsheet_row'))
        unsynced = len(posts) - synced
        return {
            'total_posts': len(posts),
            'synced': synced,
            'unsynced': unsynced,
            'health': 'green' if unsynced == 0 else ('yellow' if unsynced < 3 else 'red'),
            'last_check': datetime.now(timezone.utc).isoformat(),
        }

    # ── POST /social/schedule/sync-sheets — Manual sync trigger ──
    @router.post('/sync-sheets')
    async def sync_all_to_sheets(x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        posts = _load_scheduled()
        synced = 0
        errors = []

        for post_id, post in posts.items():
            try:
                await _trigger_sync(post, 'upsert')
                synced += 1
            except Exception as e:
                errors.append({'post_id': post_id, 'error': str(e)})

        return {
            'ok': True,
            'synced': synced,
            'errors': errors,
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }

    # ── GET /social/schedule/calendar — Calendar view ──
    @router.get('/calendar')
    async def calendar_view(x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        posts = list(_load_scheduled().values())

        # Group by date
        by_date = defaultdict(list)
        for p in posts:
            sched = p.get('scheduled_time', '')
            if sched:
                try:
                    date_str = sched[:10]  # YYYY-MM-DD
                except Exception:
                    date_str = 'unscheduled'
            else:
                date_str = 'unscheduled'
            by_date[date_str].append(p)

        # Sort dates
        sorted_dates = sorted(by_date.keys())
        calendar = []
        for d in sorted_dates:
            items = sorted(by_date[d], key=lambda p: p.get('scheduled_time') or '')
            calendar.append({'date': d, 'posts': items, 'count': len(items)})

        return {'calendar': calendar, 'total': len(posts)}

    # ── POST /social/schedule/bulk — Bulk create ──
    @router.post('/bulk')
    async def bulk_create(request: Request, x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        body = await request.json()
        entries = body.get('entries', [])
        if not entries:
            raise HTTPException(400, 'No entries provided')

        posts = _load_scheduled()
        created = []

        for entry in entries:
            post_id = entry.get('id') or _make_baas_id()
            post = _enrich_post(entry, post_id)
            posts[post_id] = post
            created.append(post)

        _save_scheduled(posts)

        # Sync all created entries
        for post in created:
            await _trigger_sync(post, 'upsert')

        log.info(f'Bulk created {len(created)} schedule entries')
        return {'ok': True, 'created': len(created), 'posts': created}

    # ── GET /social/schedule/stats — Statistics ──
    @router.get('/stats')
    async def schedule_stats(x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        posts = list(_load_scheduled().values())

        by_status = defaultdict(int)
        by_content_type = defaultdict(int)
        by_platform = defaultdict(int)
        by_date = defaultdict(int)

        for p in posts:
            by_status[p.get('status', 'unknown')] += 1
            by_content_type[p.get('content_type', 'unknown')] += 1
            by_platform[p.get('platform', 'unknown')] += 1
            sched = p.get('scheduled_time', '')
            if sched:
                by_date[sched[:10]] += 1

        return {
            'total': len(posts),
            'by_status': dict(by_status),
            'by_content_type': dict(by_content_type),
            'by_platform': dict(by_platform),
            'by_date': dict(by_date),
        }

    # ── GET /social/schedule/{id} — Get one (MUST be after specific routes) ──
    @router.get('/{post_id}')
    async def get_schedule_entry(post_id: str, x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        posts = _load_scheduled()
        if post_id not in posts:
            raise HTTPException(404, f'Post {post_id} not found')
        return {'post': posts[post_id]}

    # ── PUT /social/schedule/{id} — Update ──
    @router.put('/{post_id}')
    async def update_schedule_entry(post_id: str, request: Request, x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        body = await request.json()
        posts = _load_scheduled()
        if post_id not in posts:
            raise HTTPException(404, f'Post {post_id} not found')

        existing = posts[post_id]
        for k, v in body.items():
            if k != 'id' and v is not None:
                existing[k] = v
        existing['updated_at'] = datetime.now(timezone.utc).isoformat()
        existing['publish_status'] = existing.get('status', existing.get('publish_status', 'draft'))

        posts[post_id] = existing
        _save_scheduled(posts)

        log.info(f'Schedule updated: {post_id} -> status={existing.get("status")}')
        await _trigger_sync(existing, 'upsert')
        return {'ok': True, 'post': existing}

    # ── DELETE /social/schedule/{id} — Delete ──
    @router.delete('/{post_id}')
    async def delete_schedule_entry(post_id: str, x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        posts = _load_scheduled()
        deleted_post = posts.pop(post_id, None)
        _save_scheduled(posts)
        if deleted_post:
            await _trigger_sync(deleted_post, 'delete')
        log.info(f'Schedule deleted: {post_id}')
        return {'ok': True}

    # ── POST /social/schedule/{id}/approve — Approve ──
    @router.post('/{post_id}/approve')
    async def approve_schedule_entry(post_id: str, x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        posts = _load_scheduled()
        if post_id not in posts:
            raise HTTPException(404, f'Post {post_id} not found')

        posts[post_id]['status'] = 'approved'
        posts[post_id]['publish_status'] = 'approved'
        posts[post_id]['updated_at'] = datetime.now(timezone.utc).isoformat()
        _save_scheduled(posts)

        log.info(f'Schedule approved: {post_id}')
        await _trigger_sync(posts[post_id], 'upsert')
        return {'ok': True, 'post': posts[post_id]}

    # ── POST /social/schedule/{id}/publish — Trigger publish ──
    @router.post('/{post_id}/publish')
    async def publish_schedule_entry(post_id: str, x_api_key: str = Header(None)):
        auth_fn(x_api_key)
        posts = _load_scheduled()
        if post_id not in posts:
            raise HTTPException(404, f'Post {post_id} not found')

        post = posts[post_id]
        post['status'] = 'publishing'
        post['publish_status'] = 'publishing'
        post['updated_at'] = datetime.now(timezone.utc).isoformat()
        _save_scheduled(posts)

        # Attempt to publish via the social suite adapters
        platform = post.get('platform', 'linkedin')
        content = post.get('content', '')
        success = False
        error_msg = ''

        try:
            # Check for active session
            session_id = None
            for sid, sinfo in sessions_ref.items():
                if platform in sid.lower() or platform in str(sinfo.get('profile_name', '')).lower():
                    session_id = sid
                    break

            if not session_id:
                error_msg = f'No active {platform} session found'
            else:
                # Import the adapter
                if platform == 'linkedin':
                    from social_suite import _linkedin_post
                    result = await _linkedin_post(sessions_ref, session_id, content, auto_confirm=True)
                    success = result.get('status') in ('posted', 'drafted')
                elif platform == 'twitter':
                    from social_suite import _twitter_post
                    result = await _twitter_post(sessions_ref, session_id, content, auto_confirm=True)
                    success = result.get('status') in ('posted', 'drafted')
                else:
                    error_msg = f'No publish adapter for platform: {platform}'
        except Exception as e:
            error_msg = str(e)
            log.error(f'Publish failed for {post_id}: {e}')

        # Update status
        posts = _load_scheduled()
        if post_id in posts:
            if success:
                posts[post_id]['status'] = 'posted'
                posts[post_id]['publish_status'] = 'posted'
            else:
                posts[post_id]['status'] = 'failed'
                posts[post_id]['publish_status'] = 'failed'
                posts[post_id]['error'] = error_msg
            posts[post_id]['updated_at'] = datetime.now(timezone.utc).isoformat()
            _save_scheduled(posts)
            await _trigger_sync(posts[post_id], 'upsert')

        return {
            'ok': success,
            'post': posts.get(post_id, post),
            'error': error_msg if not success else None,
        }

    return router


def set_sync_callback(callback):
    """Register the sheet sync callback function."""
    global _sync_callback
    _sync_callback = callback
    log.info('Sheet sync callback registered')
