#!/usr/bin/env python3
"""
Google Calendar Manager for Aether

Full read/write access to Google Calendar.
- List calendars
- List events
- Create events
- Update events
- Delete events
- Check free/busy times

AUTHENTICATION PRIORITY:
1. OAuth2 token (oauth-token.json) - Full access as account owner
2. Service Account (google-drive-service-account.json) - Fallback

Run tools/gcal_oauth_setup.py to set up OAuth2 authentication with Calendar scope.
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Union
from zoneinfo import ZoneInfo

try:
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials as OAuthCredentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
except ImportError:
    print("Google libraries not installed.")
    print("Run: pip install google-auth google-auth-oauthlib google-api-python-client")
    exit(1)

# Scopes for Calendar access
SCOPES = [
    'https://www.googleapis.com/auth/calendar',           # Full calendar access
    'https://www.googleapis.com/auth/calendar.events',    # Events access
]

# Default timezone
DEFAULT_TIMEZONE = 'America/New_York'


class GCalManager:
    """Full-featured Google Calendar manager with read/write capabilities."""

    def __init__(self, verbose: bool = True, timezone: str = DEFAULT_TIMEZONE):
        self.verbose = verbose
        self.timezone = timezone
        self.base_path = Path(__file__).parent.parent
        self.creds_dir = self.base_path / ".credentials"
        self.oauth_token_path = self.creds_dir / "oauth-token-calendar.json"
        self.service_account_path = self.creds_dir / "google-drive-service-account.json"
        self.auth_type = None

        # Initialize service with best available credentials
        self.service = self._authenticate()

    def _log(self, message: str):
        """Print message if verbose mode is on."""
        if self.verbose:
            print(message)

    def _get_oauth_credentials(self) -> Optional[OAuthCredentials]:
        """Try to load OAuth2 credentials from token file."""
        if not self.oauth_token_path.exists():
            return None

        try:
            creds = OAuthCredentials.from_authorized_user_file(
                str(self.oauth_token_path), SCOPES
            )

            if creds.valid:
                return creds

            if creds.expired and creds.refresh_token:
                self._log("[AUTH] OAuth token expired, refreshing...")
                creds.refresh(Request())
                self._save_oauth_token(creds)
                self._log("[AUTH] OAuth token refreshed successfully")
                return creds

            return None

        except Exception as e:
            self._log(f"[AUTH] OAuth token error: {e}")
            return None

    def _save_oauth_token(self, creds: OAuthCredentials):
        """Save refreshed OAuth credentials."""
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': list(creds.scopes) if creds.scopes else SCOPES,
        }

        with open(self.oauth_token_path, 'w') as f:
            json.dump(token_data, f, indent=2)

        os.chmod(self.oauth_token_path, 0o600)

    def _get_service_account_credentials(self):
        """Load service account credentials."""
        if not self.service_account_path.exists():
            return None

        try:
            return service_account.Credentials.from_service_account_file(
                str(self.service_account_path), scopes=SCOPES
            )
        except Exception as e:
            self._log(f"[AUTH] Service account error: {e}")
            return None

    def _authenticate(self):
        """Authenticate with Google Calendar using best available credentials."""
        # Try OAuth2 first (preferred)
        oauth_creds = self._get_oauth_credentials()
        if oauth_creds:
            self.auth_type = "oauth2"
            self._log("[AUTH] Using OAuth2 credentials (owner access)")
            return build('calendar', 'v3', credentials=oauth_creds)

        # Fall back to service account
        sa_creds = self._get_service_account_credentials()
        if sa_creds:
            self.auth_type = "service_account"
            self._log("[AUTH] Using Service Account credentials")
            self._log("[AUTH] TIP: Run 'python tools/gcal_oauth_setup.py' for owner access")
            return build('calendar', 'v3', credentials=sa_creds)

        raise Exception(
            "No valid credentials found!\n"
            f"  OAuth token: {self.oauth_token_path} (not found)\n"
            f"  Service account: {self.service_account_path} (not found)\n"
            "\nRun: python tools/gcal_oauth_setup.py to set up OAuth authentication"
        )

    def get_auth_info(self) -> Dict:
        """Return information about current authentication."""
        return {
            'auth_type': self.auth_type,
            'oauth_token_exists': self.oauth_token_path.exists(),
            'service_account_exists': self.service_account_path.exists(),
            'timezone': self.timezone,
        }

    # ==================== CALENDAR OPERATIONS ====================

    def list_calendars(self) -> List[Dict]:
        """List all calendars accessible to the account."""
        calendar_list = self.service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])

        result = []
        for cal in calendars:
            result.append({
                'id': cal['id'],
                'summary': cal.get('summary', 'Untitled'),
                'primary': cal.get('primary', False),
                'access_role': cal.get('accessRole', 'unknown'),
                'time_zone': cal.get('timeZone', 'unknown'),
            })

        return result

    def get_primary_calendar_id(self) -> str:
        """Get the ID of the primary calendar."""
        calendars = self.list_calendars()
        for cal in calendars:
            if cal.get('primary'):
                return cal['id']
        return 'primary'  # Fallback

    # ==================== EVENT OPERATIONS ====================

    def list_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 50,
        search_query: Optional[str] = None
    ) -> List[Dict]:
        """
        List events from a calendar.

        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Start time filter (default: now)
            time_max: End time filter (default: 7 days from now)
            max_results: Maximum number of events to return
            search_query: Optional text search query
        """
        if time_min is None:
            time_min = datetime.now(ZoneInfo(self.timezone))
        if time_max is None:
            time_max = time_min + timedelta(days=7)

        # Convert to RFC3339 format
        time_min_str = time_min.isoformat()
        time_max_str = time_max.isoformat()

        kwargs = {
            'calendarId': calendar_id,
            'timeMin': time_min_str,
            'timeMax': time_max_str,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime',
        }

        if search_query:
            kwargs['q'] = search_query

        events_result = self.service.events().list(**kwargs).execute()
        events = events_result.get('items', [])

        result = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            result.append({
                'id': event['id'],
                'summary': event.get('summary', 'No Title'),
                'description': event.get('description', ''),
                'start': start,
                'end': end,
                'location': event.get('location', ''),
                'attendees': [a.get('email') for a in event.get('attendees', [])],
                'html_link': event.get('htmlLink', ''),
                'status': event.get('status', 'confirmed'),
            })

        return result

    def get_event(self, event_id: str, calendar_id: str = 'primary') -> Dict:
        """Get a specific event by ID."""
        event = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        return {
            'id': event['id'],
            'summary': event.get('summary', 'No Title'),
            'description': event.get('description', ''),
            'start': start,
            'end': end,
            'location': event.get('location', ''),
            'attendees': [a.get('email') for a in event.get('attendees', [])],
            'html_link': event.get('htmlLink', ''),
            'status': event.get('status', 'confirmed'),
            'created': event.get('created'),
            'updated': event.get('updated'),
            'creator': event.get('creator', {}).get('email'),
            'organizer': event.get('organizer', {}).get('email'),
        }

    def create_event(
        self,
        summary: str,
        start: Union[datetime, str],
        end: Optional[Union[datetime, str]] = None,
        duration_minutes: int = 60,
        description: str = '',
        location: str = '',
        attendees: Optional[List[str]] = None,
        calendar_id: str = 'primary',
        send_notifications: bool = True,
        reminders: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Create a new calendar event.

        Args:
            summary: Event title
            start: Start time (datetime or ISO string)
            end: End time (if not provided, uses duration_minutes)
            duration_minutes: Duration in minutes (default: 60)
            description: Event description
            location: Event location
            attendees: List of email addresses to invite
            calendar_id: Calendar ID (default: 'primary')
            send_notifications: Send email notifications to attendees
            reminders: List of reminders, e.g., [{'method': 'popup', 'minutes': 10}]

        Returns:
            Created event details including ID and link
        """
        # Handle start time
        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace('Z', '+00:00'))

        if start.tzinfo is None:
            start = start.replace(tzinfo=ZoneInfo(self.timezone))

        # Handle end time
        if end is None:
            end = start + timedelta(minutes=duration_minutes)
        elif isinstance(end, str):
            end = datetime.fromisoformat(end.replace('Z', '+00:00'))

        if end.tzinfo is None:
            end = end.replace(tzinfo=ZoneInfo(self.timezone))

        event_body = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': self.timezone,
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': self.timezone,
            },
        }

        if attendees:
            event_body['attendees'] = [{'email': email} for email in attendees]

        if reminders:
            event_body['reminders'] = {
                'useDefault': False,
                'overrides': reminders,
            }

        event = self.service.events().insert(
            calendarId=calendar_id,
            body=event_body,
            sendNotifications=send_notifications,
        ).execute()

        self._log(f"[{datetime.now()}] Created event: {summary}")
        self._log(f"  -> ID: {event.get('id')}")
        self._log(f"  -> Link: {event.get('htmlLink')}")

        return {
            'id': event['id'],
            'summary': event.get('summary'),
            'start': event['start'].get('dateTime'),
            'end': event['end'].get('dateTime'),
            'html_link': event.get('htmlLink'),
            'status': event.get('status'),
        }

    def create_all_day_event(
        self,
        summary: str,
        date: Union[datetime, str],
        end_date: Optional[Union[datetime, str]] = None,
        description: str = '',
        location: str = '',
        calendar_id: str = 'primary',
    ) -> Dict:
        """
        Create an all-day event.

        Args:
            summary: Event title
            date: Event date (datetime or 'YYYY-MM-DD' string)
            end_date: End date for multi-day events
            description: Event description
            location: Event location
            calendar_id: Calendar ID (default: 'primary')
        """
        if isinstance(date, datetime):
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = date

        if end_date is None:
            # Single day event - end date is next day (exclusive)
            end_date_str = (datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        elif isinstance(end_date, datetime):
            end_date_str = (end_date + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            end_date_str = end_date

        event_body = {
            'summary': summary,
            'description': description,
            'location': location,
            'start': {'date': date_str},
            'end': {'date': end_date_str},
        }

        event = self.service.events().insert(
            calendarId=calendar_id,
            body=event_body,
        ).execute()

        self._log(f"[{datetime.now()}] Created all-day event: {summary}")

        return {
            'id': event['id'],
            'summary': event.get('summary'),
            'start': event['start'].get('date'),
            'end': event['end'].get('date'),
            'html_link': event.get('htmlLink'),
        }

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        start: Optional[Union[datetime, str]] = None,
        end: Optional[Union[datetime, str]] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        calendar_id: str = 'primary',
        send_notifications: bool = True,
    ) -> Dict:
        """
        Update an existing event.

        Only provided fields will be updated.
        """
        # Get existing event
        event = self.service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()

        # Update fields
        if summary is not None:
            event['summary'] = summary
        if description is not None:
            event['description'] = description
        if location is not None:
            event['location'] = location

        if start is not None:
            if isinstance(start, str):
                start = datetime.fromisoformat(start.replace('Z', '+00:00'))
            if start.tzinfo is None:
                start = start.replace(tzinfo=ZoneInfo(self.timezone))
            event['start'] = {
                'dateTime': start.isoformat(),
                'timeZone': self.timezone,
            }

        if end is not None:
            if isinstance(end, str):
                end = datetime.fromisoformat(end.replace('Z', '+00:00'))
            if end.tzinfo is None:
                end = end.replace(tzinfo=ZoneInfo(self.timezone))
            event['end'] = {
                'dateTime': end.isoformat(),
                'timeZone': self.timezone,
            }

        if attendees is not None:
            event['attendees'] = [{'email': email} for email in attendees]

        updated_event = self.service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event,
            sendNotifications=send_notifications,
        ).execute()

        self._log(f"[{datetime.now()}] Updated event: {updated_event.get('summary')}")

        return {
            'id': updated_event['id'],
            'summary': updated_event.get('summary'),
            'start': updated_event['start'].get('dateTime', updated_event['start'].get('date')),
            'end': updated_event['end'].get('dateTime', updated_event['end'].get('date')),
            'html_link': updated_event.get('htmlLink'),
        }

    def delete_event(
        self,
        event_id: str,
        calendar_id: str = 'primary',
        send_notifications: bool = True,
    ) -> bool:
        """Delete an event."""
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendNotifications=send_notifications,
        ).execute()

        self._log(f"[{datetime.now()}] Deleted event: {event_id}")
        return True

    # ==================== FREE/BUSY OPERATIONS ====================

    def get_free_busy(
        self,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        calendar_ids: Optional[List[str]] = None,
    ) -> Dict:
        """
        Get free/busy information for calendars.

        Args:
            time_min: Start of time range (default: now)
            time_max: End of time range (default: 7 days from now)
            calendar_ids: List of calendar IDs to check (default: primary)

        Returns:
            Dict with busy times for each calendar
        """
        if time_min is None:
            time_min = datetime.now(ZoneInfo(self.timezone))
        if time_max is None:
            time_max = time_min + timedelta(days=7)
        if calendar_ids is None:
            calendar_ids = ['primary']

        body = {
            'timeMin': time_min.isoformat(),
            'timeMax': time_max.isoformat(),
            'items': [{'id': cal_id} for cal_id in calendar_ids],
        }

        freebusy = self.service.freebusy().query(body=body).execute()

        result = {}
        for cal_id, info in freebusy.get('calendars', {}).items():
            busy_times = []
            for busy in info.get('busy', []):
                busy_times.append({
                    'start': busy['start'],
                    'end': busy['end'],
                })
            result[cal_id] = {
                'busy': busy_times,
                'errors': info.get('errors', []),
            }

        return result

    def find_free_slots(
        self,
        duration_minutes: int = 60,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        work_hours: tuple = (9, 17),
        calendar_id: str = 'primary',
    ) -> List[Dict]:
        """
        Find available time slots in the calendar.

        Args:
            duration_minutes: Required duration of free slot
            time_min: Start of search range (default: now)
            time_max: End of search range (default: 7 days)
            work_hours: Tuple of (start_hour, end_hour) for business hours
            calendar_id: Calendar to check

        Returns:
            List of available slots with start/end times
        """
        if time_min is None:
            time_min = datetime.now(ZoneInfo(self.timezone))
        if time_max is None:
            time_max = time_min + timedelta(days=7)

        # Get busy times
        freebusy = self.get_free_busy(time_min, time_max, [calendar_id])
        busy_times = freebusy.get(calendar_id, {}).get('busy', [])

        # Parse busy times
        busy_ranges = []
        for busy in busy_times:
            busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            busy_ranges.append((busy_start, busy_end))

        # Find free slots
        free_slots = []
        current = time_min

        while current < time_max:
            # Check if within work hours
            if current.hour < work_hours[0]:
                current = current.replace(hour=work_hours[0], minute=0, second=0, microsecond=0)
                continue
            if current.hour >= work_hours[1]:
                current = (current + timedelta(days=1)).replace(
                    hour=work_hours[0], minute=0, second=0, microsecond=0
                )
                continue

            # Skip weekends
            if current.weekday() >= 5:
                current = current + timedelta(days=1)
                current = current.replace(hour=work_hours[0], minute=0, second=0, microsecond=0)
                continue

            # Check if slot is free
            slot_end = current + timedelta(minutes=duration_minutes)

            # Don't extend past work hours
            if slot_end.hour > work_hours[1] or (slot_end.hour == work_hours[1] and slot_end.minute > 0):
                current = (current + timedelta(days=1)).replace(
                    hour=work_hours[0], minute=0, second=0, microsecond=0
                )
                continue

            is_free = True
            for busy_start, busy_end in busy_ranges:
                # Check overlap
                if current < busy_end and slot_end > busy_start:
                    is_free = False
                    # Jump to end of this busy period
                    current = busy_end
                    break

            if is_free:
                free_slots.append({
                    'start': current.isoformat(),
                    'end': slot_end.isoformat(),
                })
                current = slot_end

            # Safety check to prevent infinite loop
            if len(free_slots) >= 20:
                break

        return free_slots

    # ==================== QUICK ADD ====================

    def quick_add(self, text: str, calendar_id: str = 'primary') -> Dict:
        """
        Create an event using natural language (Google's Quick Add).

        Examples:
            "Meeting with Bob tomorrow at 3pm"
            "Lunch at noon on Friday"
            "Call with client next Monday 10am-11am"
        """
        event = self.service.events().quickAdd(
            calendarId=calendar_id,
            text=text,
        ).execute()

        self._log(f"[{datetime.now()}] Quick added: {event.get('summary')}")

        return {
            'id': event['id'],
            'summary': event.get('summary'),
            'start': event['start'].get('dateTime', event['start'].get('date')),
            'end': event['end'].get('dateTime', event['end'].get('date')),
            'html_link': event.get('htmlLink'),
        }


# ==================== CLI INTERFACE ====================

def main():
    """CLI for Google Calendar Manager."""
    import sys

    if len(sys.argv) < 2:
        print("Google Calendar Manager for Aether")
        print("\nUsage:")
        print("  python gcal_manager.py auth-info              # Show authentication status")
        print("  python gcal_manager.py calendars              # List all calendars")
        print("  python gcal_manager.py events [days]          # List upcoming events")
        print("  python gcal_manager.py today                  # List today's events")
        print("  python gcal_manager.py create <title> <time>  # Create event")
        print("  python gcal_manager.py quick '<text>'         # Quick add (natural language)")
        print("  python gcal_manager.py free [duration_mins]   # Find free slots")
        print("\nExamples:")
        print("  python gcal_manager.py events 14              # Events for next 14 days")
        print("  python gcal_manager.py create 'Team Meeting' '2026-02-12 10:00'")
        print("  python gcal_manager.py quick 'Lunch with Bob tomorrow at noon'")
        return

    command = sys.argv[1]

    try:
        manager = GCalManager()
    except Exception as e:
        print(f"Authentication failed: {e}")
        print("\nTo set up Calendar authentication:")
        print("1. Run: python tools/gcal_oauth_setup.py")
        print("2. Follow the browser prompts to authorize")
        return

    if command == 'auth-info':
        info = manager.get_auth_info()
        print("Authentication Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")

    elif command == 'calendars':
        print("Your Calendars:")
        calendars = manager.list_calendars()
        for cal in calendars:
            primary = " (PRIMARY)" if cal['primary'] else ""
            print(f"  - {cal['summary']}{primary}")
            print(f"    ID: {cal['id']}")

    elif command == 'events':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print(f"Events for next {days} days:")

        time_max = datetime.now(ZoneInfo(DEFAULT_TIMEZONE)) + timedelta(days=days)
        events = manager.list_events(time_max=time_max)

        if not events:
            print("  No events found.")
        for event in events:
            print(f"\n  {event['summary']}")
            print(f"    When: {event['start']} - {event['end']}")
            if event['location']:
                print(f"    Where: {event['location']}")

    elif command == 'today':
        print("Today's Events:")
        now = datetime.now(ZoneInfo(DEFAULT_TIMEZONE))
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        events = manager.list_events(time_min=start, time_max=end)

        if not events:
            print("  No events today.")
        for event in events:
            print(f"\n  {event['summary']}")
            print(f"    When: {event['start']} - {event['end']}")

    elif command == 'create' and len(sys.argv) >= 4:
        title = sys.argv[2]
        time_str = sys.argv[3]

        start = datetime.fromisoformat(time_str)
        event = manager.create_event(summary=title, start=start)
        print(f"Created: {event['summary']}")
        print(f"Link: {event['html_link']}")

    elif command == 'quick' and len(sys.argv) >= 3:
        text = sys.argv[2]
        event = manager.quick_add(text)
        print(f"Created: {event['summary']}")
        print(f"When: {event['start']}")
        print(f"Link: {event['html_link']}")

    elif command == 'free':
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        print(f"Finding {duration}-minute free slots:")

        slots = manager.find_free_slots(duration_minutes=duration)

        if not slots:
            print("  No free slots found.")
        for slot in slots[:10]:
            print(f"  {slot['start']} - {slot['end']}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
