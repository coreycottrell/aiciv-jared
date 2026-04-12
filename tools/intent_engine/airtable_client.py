"""
Airtable Client for Experiential Intent Engine
"""
import requests
from datetime import datetime, timezone
from typing import List, Dict, Optional
from .config import (
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    PEOPLE_TABLE,
    SIGNALS_TABLE,
    COMPANIES_TABLE,
)

BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}"

def _headers():
    return {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }


def get_all_people(filter_formula: Optional[str] = None) -> List[Dict]:
    """Get all people from People table"""
    url = f"{BASE_URL}/{PEOPLE_TABLE}"
    params = {}
    if filter_formula:
        params["filterByFormula"] = filter_formula

    all_records = []
    offset = None

    while True:
        if offset:
            params["offset"] = offset

        resp = requests.get(url, headers=_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()

        all_records.extend(data.get("records", []))
        offset = data.get("offset")

        if not offset:
            break

    return all_records


def get_people_with_linkedin() -> List[Dict]:
    """Get people who have LinkedIn URLs"""
    return get_all_people(filter_formula="NOT({LinkedIn URL} = '')")


def get_people_with_twitter() -> List[Dict]:
    """Get people who have Twitter handles or Twitter URLs"""
    # Support both Twitter Handle field and Twitter URL field
    # This allows flexibility in how Twitter info is stored in Airtable
    return get_all_people(
        filter_formula="OR(NOT({Twitter Handle} = ''), NOT({Twitter URL} = ''))"
    )


def get_ready_prospects(limit: int = 10) -> List[Dict]:
    """Get top prospects with READY status, sorted by score"""
    url = f"{BASE_URL}/{PEOPLE_TABLE}"
    params = {
        "filterByFormula": '{Readiness Flag (formula)} = "🟢 READY"',
        "sort[0][field]": "Rolling Intent Score (formula)",
        "sort[0][direction]": "desc",
        "maxRecords": limit
    }

    resp = requests.get(url, headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json().get("records", [])


def get_warm_prospects(limit: int = 10) -> List[Dict]:
    """Get prospects with WARM status"""
    url = f"{BASE_URL}/{PEOPLE_TABLE}"
    params = {
        "filterByFormula": '{Readiness Flag (formula)} = "🟡 WARM"',
        "sort[0][field]": "Rolling Intent Score (formula)",
        "sort[0][direction]": "desc",
        "maxRecords": limit
    }

    resp = requests.get(url, headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json().get("records", [])


def create_signal(
    signal_type: str,
    signal_strength: int,
    source: str,
    linkedin_url: str,
    person_record_id: Optional[str] = None,
    signal_timestamp: Optional[str] = None,
) -> Dict:
    """
    Create a new signal record.

    Args:
        signal_type: Type of signal (e.g., 'posted_about_launch')
        signal_strength: Strength score 1-10
        source: Signal source (e.g., 'LinkedIn', 'Twitter')
        linkedin_url: URL of the LinkedIn profile
        person_record_id: Optional Airtable record ID to link to
        signal_timestamp: Optional ISO timestamp of when the signal occurred
                         (e.g., when post was published). Defaults to current time.
    """
    url = f"{BASE_URL}/{SIGNALS_TABLE}"

    # Use provided timestamp or default to now
    # The signal timestamp should be when the activity happened (post date, etc.)
    # NOT when we detected it
    if signal_timestamp:
        timestamp = signal_timestamp
    else:
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    fields = {
        "Signal Type": signal_type,
        "Signal Strength": signal_strength,
        "Source": source,
        "LinkedIn URL": linkedin_url,
        "Signal Timestamp": timestamp,
    }

    # Link to person if provided
    if person_record_id:
        fields["Name"] = [person_record_id]

    payload = {"fields": fields}

    resp = requests.post(url, headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def update_person_last_checked(person_record_id: str) -> Dict:
    """
    Update the Last Checked timestamp on a person record.

    This should be called when we check a person's profile for signals.
    """
    url = f"{BASE_URL}/{PEOPLE_TABLE}/{person_record_id}"

    fields = {
        "Last Checked": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
    }

    payload = {"fields": fields}

    resp = requests.patch(url, headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def create_person(
    name: str,
    linkedin_url: str,
    title: Optional[str] = None,
    seniority: Optional[str] = None,
    function_type: Optional[str] = None,
) -> Dict:
    """Create a new person record"""
    url = f"{BASE_URL}/{PEOPLE_TABLE}"

    fields = {
        "Name": name,
        "LinkedIn URL": linkedin_url,
    }

    if title:
        fields["Title"] = title
    if seniority:
        fields["Seniority"] = seniority
    if function_type:
        fields["Function Type"] = function_type

    payload = {"fields": fields}

    resp = requests.post(url, headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def find_person_by_linkedin(linkedin_url: str) -> Optional[Dict]:
    """Find a person by their LinkedIn URL"""
    records = get_all_people(
        filter_formula=f'{{LinkedIn URL}} = "{linkedin_url}"'
    )
    return records[0] if records else None


def get_recent_signals(hours: int = 24) -> List[Dict]:
    """Get signals from the last N hours"""
    url = f"{BASE_URL}/{SIGNALS_TABLE}"
    params = {
        "filterByFormula": f"DATETIME_DIFF(NOW(), {{Signal Timestamp}}, 'hours') < {hours}",
        "sort[0][field]": "Signal Timestamp",
        "sort[0][direction]": "desc",
    }

    resp = requests.get(url, headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json().get("records", [])


def update_company(company_record_id: str, fields: Dict) -> Dict:
    """
    Update a company record with the given fields.

    Args:
        company_record_id: Airtable record ID for the company
        fields: Dict of field names and values to update

    Returns:
        Updated record data
    """
    url = f"{BASE_URL}/{COMPANIES_TABLE}/{company_record_id}"

    payload = {"fields": fields}

    resp = requests.patch(url, headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def count_by_status() -> Dict[str, int]:
    """Count prospects by readiness status"""
    all_people = get_all_people()

    counts = {"ready": 0, "warm": 0, "cold": 0}

    for person in all_people:
        flag = person.get("fields", {}).get("Readiness Flag (formula)", "")
        if "READY" in flag:
            counts["ready"] += 1
        elif "WARM" in flag:
            counts["warm"] += 1
        else:
            counts["cold"] += 1

    return counts


def is_contact_inactive(
    person: Dict,
    signals: List[Dict],
    inactive_days: int = 90,
    grace_period_days: int = 30,
) -> bool:
    """
    Determine if a contact is inactive based on signal activity.

    Args:
        person: Person record from Airtable
        signals: List of signal records linked to this person
        inactive_days: Number of days without signals to be considered inactive
        grace_period_days: Don't remove people added within this many days

    Returns:
        True if the contact should be considered inactive, False otherwise

    Business Rules:
        - "Active" = has at least 1 signal in the past inactive_days
        - "Inactive" = zero signals in inactive_days+ days
        - If someone was added recently (< grace_period_days) with no signals,
          don't remove them - give them a chance
    """
    now = datetime.now(timezone.utc)

    # Check grace period: if person was added recently, protect them
    created_time_str = person.get("createdTime", "")
    if created_time_str:
        try:
            created_time = datetime.fromisoformat(created_time_str.replace("Z", "+00:00"))
            days_since_created = (now - created_time).days
            if days_since_created < grace_period_days:
                return False  # Protected - too new to remove
        except (ValueError, TypeError):
            pass  # If we can't parse, continue with signal check

    # If no signals, check if they've been around long enough
    if not signals:
        # Already past grace period check above, so if no signals = inactive
        return True

    # Check most recent signal timestamp
    most_recent_signal_time = None
    for signal in signals:
        timestamp_str = signal.get("fields", {}).get("Signal Timestamp", "")
        if timestamp_str:
            try:
                signal_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                if most_recent_signal_time is None or signal_time > most_recent_signal_time:
                    most_recent_signal_time = signal_time
            except (ValueError, TypeError):
                continue

    if most_recent_signal_time is None:
        # No valid signal timestamps found
        return True

    # Check if most recent signal is within the inactive_days threshold
    days_since_signal = (now - most_recent_signal_time).days
    return days_since_signal >= inactive_days


def get_signals_for_person(person_record_id: str) -> List[Dict]:
    """
    Get all signals linked to a specific person.

    Args:
        person_record_id: Airtable record ID of the person

    Returns:
        List of signal records
    """
    url = f"{BASE_URL}/{SIGNALS_TABLE}"
    params = {
        "filterByFormula": f'FIND("{person_record_id}", ARRAYJOIN({{Name}}))',
    }

    all_records = []
    offset = None

    while True:
        if offset:
            params["offset"] = offset

        resp = requests.get(url, headers=_headers(), params=params)
        resp.raise_for_status()
        data = resp.json()

        all_records.extend(data.get("records", []))
        offset = data.get("offset")

        if not offset:
            break

    return all_records


def archive_person(person_record_id: str, reason: str = "inactive") -> Dict:
    """
    Archive a person (soft-delete) instead of hard deleting.

    Args:
        person_record_id: Airtable record ID to archive
        reason: Reason for archiving (for logging/audit)

    Returns:
        Updated record
    """
    url = f"{BASE_URL}/{PEOPLE_TABLE}/{person_record_id}"

    fields = {
        "Status": "Archived",
        "Archive Reason": reason,
        "Archived At": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    }

    payload = {"fields": fields}

    resp = requests.patch(url, headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def delete_person(person_record_id: str) -> Dict:
    """
    Hard delete a person record from Airtable.

    Args:
        person_record_id: Airtable record ID to delete

    Returns:
        Deletion confirmation
    """
    url = f"{BASE_URL}/{PEOPLE_TABLE}/{person_record_id}"

    resp = requests.delete(url, headers=_headers())
    resp.raise_for_status()
    return resp.json()


def get_inactive_people(
    inactive_days: int = 90,
    grace_period_days: int = 30,
) -> List[Dict]:
    """
    Get all people who are considered inactive.

    Args:
        inactive_days: Number of days without signals to be considered inactive
        grace_period_days: Protect people added within this many days

    Returns:
        List of inactive person records
    """
    all_people = get_all_people()
    inactive_people = []

    for person in all_people:
        person_id = person.get("id")
        if not person_id:
            continue

        signals = get_signals_for_person(person_id)

        if is_contact_inactive(
            person, signals,
            inactive_days=inactive_days,
            grace_period_days=grace_period_days
        ):
            inactive_people.append(person)

    return inactive_people


def cleanup_inactive(
    days: int = 90,
    grace_period_days: int = 30,
    dry_run: bool = True,
) -> Dict:
    """
    Clean up inactive contacts by archiving them.

    Args:
        days: Number of days without signals to be considered inactive
        grace_period_days: Protect people added within this many days
        dry_run: If True, only report what would be removed without actually removing

    Returns:
        Summary dict with:
            - would_remove: Count of people that would be removed
            - removed: Count of people actually removed (0 if dry_run)
            - inactive_days: The days threshold used
            - people: List of people affected (with names)
    """
    inactive_people = get_inactive_people(
        inactive_days=days,
        grace_period_days=grace_period_days
    )

    result = {
        "would_remove": len(inactive_people),
        "removed": 0,
        "inactive_days": days,
        "grace_period_days": grace_period_days,
        "people": [
            {
                "id": p["id"],
                "name": p.get("fields", {}).get("Name", "Unknown"),
            }
            for p in inactive_people
        ],
    }

    if not dry_run:
        for person in inactive_people:
            try:
                archive_person(person["id"], reason=f"inactive_{days}_days")
                result["removed"] += 1
            except Exception as e:
                print(f"Error archiving {person['id']}: {e}")

    return result


if __name__ == "__main__":
    # Test the client
    print("Testing Airtable Client...")

    print("\n1. Getting all people with LinkedIn:")
    people = get_people_with_linkedin()
    print(f"   Found {len(people)} people")

    print("\n2. Getting ready prospects:")
    ready = get_ready_prospects()
    print(f"   Found {len(ready)} ready prospects")

    print("\n3. Counting by status:")
    counts = count_by_status()
    print(f"   Ready: {counts['ready']}, Warm: {counts['warm']}, Cold: {counts['cold']}")

    print("\n✅ Airtable client working!")
