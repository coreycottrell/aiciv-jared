#!/usr/bin/env python3
"""
TTS Audio Assembler for Blog Posts
Monitors async TTS jobs, retries failures with shorter chunks,
downloads all audio, and concatenates with ffmpeg.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error

TTS_BASE = "http://37.27.237.109:8950"
API_KEY = "purebrain-tts-2026"
VOICE = "aether"
FORMAT = "mp3"
MAX_CHUNK_LEN = 400  # chars per chunk for retries
POLL_INTERVAL = 30   # seconds between polls
MAX_WAIT = 7200      # 2 hours max wait
WORK_DIR = "/tmp/tts_assembly"

# Blog output paths
OUTPUT_PATHS = [
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/who-do-you-learn-from-when-youre-ahead/audio.mp3",
    "/home/jared/projects/AI-CIV/aether/exports/cf-pages-deploy/blog/when-the-playbook-runs-out-authoring-the-field-of-agentic-ai/audio.mp3",
]

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def api_get(path):
    try:
        resp = urllib.request.urlopen(f"{TTS_BASE}{path}", timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        log(f"API GET {path} failed: {e}")
        return None

def api_post(path, data):
    try:
        req = urllib.request.Request(
            f"{TTS_BASE}{path}",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )
        resp = urllib.request.urlopen(req, timeout=30)
        return json.loads(resp.read())
    except Exception as e:
        log(f"API POST {path} failed: {e}")
        return None

def download_audio(job_id, output_path):
    try:
        resp = urllib.request.urlopen(f"{TTS_BASE}/tts/jobs/{job_id}/audio", timeout=60)
        with open(output_path, 'wb') as f:
            f.write(resp.read())
        size = os.path.getsize(output_path)
        log(f"Downloaded {job_id[:12]}... -> {output_path} ({size} bytes)")
        return size > 0
    except Exception as e:
        log(f"Download failed for {job_id}: {e}")
        return False

def chunk_text(text, max_len=MAX_CHUNK_LEN):
    """Split text into chunks at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 1 > max_len and current:
            chunks.append(current.strip())
            current = s
        else:
            current = current + " " + s if current else s
    if current.strip():
        chunks.append(current.strip())
    return chunks

def submit_chunk(text):
    """Submit a single TTS chunk and return job_id."""
    result = api_post("/tts/async", {
        "text": text,
        "voice": VOICE,
        "format": FORMAT,
        "api_key": API_KEY
    })
    if result and "job_id" in result:
        return result["job_id"]
    return None

def get_all_jobs():
    data = api_get("/tts/jobs")
    if data:
        return data.get("jobs", [])
    return []

def get_newer_batch_jobs():
    """Get the 30 jobs from the newer batch (created_at > 1774976280)."""
    jobs = get_all_jobs()
    newer = [j for j in jobs if j['created_at'] > 1774976280]
    return sorted(newer, key=lambda x: x['created_at'])

def wait_for_jobs(job_ids, max_wait=MAX_WAIT):
    """Poll until all specified jobs are done/failed."""
    start = time.time()
    while time.time() - start < max_wait:
        jobs = get_all_jobs()
        job_map = {j['job_id']: j for j in jobs}

        statuses = {}
        for jid in job_ids:
            if jid in job_map:
                statuses[jid] = job_map[jid]['status']
            else:
                statuses[jid] = 'unknown'

        done_count = sum(1 for s in statuses.values() if s == 'done')
        failed_count = sum(1 for s in statuses.values() if s == 'failed')
        processing = sum(1 for s in statuses.values() if s == 'processing')
        queued = sum(1 for s in statuses.values() if s == 'queued')

        elapsed = int(time.time() - start)
        log(f"Progress: {done_count} done, {failed_count} failed, {processing} processing, {queued} queued [{elapsed}s elapsed]")

        if queued == 0 and processing == 0:
            return statuses

        time.sleep(POLL_INTERVAL)

    log("MAX WAIT exceeded!")
    jobs = get_all_jobs()
    job_map = {j['job_id']: j for j in jobs}
    return {jid: job_map.get(jid, {}).get('status', 'unknown') for jid in job_ids}

def main():
    os.makedirs(WORK_DIR, exist_ok=True)

    log("=== TTS Audio Assembler Starting ===")

    # Step 1: Get the newer batch of 30 jobs
    newer_jobs = get_newer_batch_jobs()
    log(f"Found {len(newer_jobs)} jobs in newer batch")

    if not newer_jobs:
        log("ERROR: No newer batch jobs found! Need to submit fresh chunks.")
        # Read the clean text and submit
        with open('/tmp/blog_tts_clean.txt', 'r') as f:
            text = f.read()
        chunks = chunk_text(text, MAX_CHUNK_LEN)
        log(f"Submitting {len(chunks)} chunks...")
        newer_jobs = []
        for i, chunk in enumerate(chunks):
            jid = submit_chunk(chunk)
            if jid:
                log(f"  Chunk {i+1}/{len(chunks)}: {jid[:12]}... ({len(chunk)} chars)")
                newer_jobs.append({'job_id': jid, 'created_at': time.time()})
            else:
                log(f"  FAILED to submit chunk {i+1}")
            time.sleep(0.5)

    job_ids = [j['job_id'] for j in newer_jobs]

    # Step 2: Also need to wait for older queued/processing jobs to clear
    all_jobs = get_all_jobs()
    older_active = [j for j in all_jobs if j['created_at'] < 1774976280 and j['status'] in ('queued', 'processing')]
    if older_active:
        log(f"Waiting for {len(older_active)} older jobs to clear first...")

    # Step 3: Wait for all our jobs to complete
    log("Waiting for all jobs to complete...")
    final_statuses = wait_for_jobs(job_ids)

    done_ids = [jid for jid, s in final_statuses.items() if s == 'done']
    failed_ids = [jid for jid, s in final_statuses.items() if s == 'failed']

    log(f"Results: {len(done_ids)} done, {len(failed_ids)} failed")

    # Step 4: Retry failed chunks with shorter text
    if failed_ids:
        log(f"Retrying {len(failed_ids)} failed chunks with shorter text...")
        retry_job_ids = []
        for fid in failed_ids:
            # Get the original text
            detail = api_get(f"/tts/jobs/{fid}")
            if detail and 'text' in detail:
                orig_text = detail['text']
                # Re-chunk at 200 chars
                sub_chunks = chunk_text(orig_text, 200)
                log(f"  Re-chunking {fid[:12]}... into {len(sub_chunks)} sub-chunks")
                for sc in sub_chunks:
                    new_jid = submit_chunk(sc)
                    if new_jid:
                        retry_job_ids.append(new_jid)
                    time.sleep(0.5)

        if retry_job_ids:
            log(f"Waiting for {len(retry_job_ids)} retry jobs...")
            retry_statuses = wait_for_jobs(retry_job_ids)
            retry_done = [jid for jid, s in retry_statuses.items() if s == 'done']
            retry_failed = [jid for jid, s in retry_statuses.items() if s == 'failed']
            log(f"Retry results: {len(retry_done)} done, {len(retry_failed)} failed")

            # Build final ordered list: replace failed original with retry results
            # This is complex - we need to maintain order
            # For simplicity, insert retry results at the position of the failed job
            all_ordered_ids = []
            retry_idx = 0
            for jid in job_ids:
                if jid in done_ids:
                    all_ordered_ids.append(jid)
                elif jid in failed_ids:
                    # Get retry jobs for this failed chunk
                    detail = api_get(f"/tts/jobs/{jid}")
                    orig_text = detail.get('text', '') if detail else ''
                    sub_count = len(chunk_text(orig_text, 200))
                    for _ in range(sub_count):
                        if retry_idx < len(retry_job_ids):
                            if retry_job_ids[retry_idx] in retry_done:
                                all_ordered_ids.append(retry_job_ids[retry_idx])
                            retry_idx += 1
            job_ids_final = all_ordered_ids
        else:
            job_ids_final = done_ids
    else:
        job_ids_final = [jid for jid in job_ids if jid in done_ids]

    if not job_ids_final:
        log("ERROR: No successful audio chunks! Aborting.")
        sys.exit(1)

    # Step 5: Download all audio chunks in order
    log(f"Downloading {len(job_ids_final)} audio chunks...")
    chunk_files = []
    for i, jid in enumerate(job_ids_final):
        outpath = os.path.join(WORK_DIR, f"chunk_{i:03d}.mp3")
        if download_audio(jid, outpath):
            chunk_files.append(outpath)
        else:
            log(f"WARNING: Failed to download chunk {i} ({jid[:12]}...)")

    if not chunk_files:
        log("ERROR: No audio files downloaded! Aborting.")
        sys.exit(1)

    log(f"Downloaded {len(chunk_files)} audio chunks")

    # Step 6: Concatenate with ffmpeg
    filelist_path = os.path.join(WORK_DIR, "filelist.txt")
    with open(filelist_path, 'w') as f:
        for cf in chunk_files:
            f.write(f"file '{cf}'\n")

    output_temp = os.path.join(WORK_DIR, "final_audio.mp3")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", filelist_path, "-c", "copy", output_temp
    ]
    log(f"Concatenating with ffmpeg...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"ffmpeg concat failed: {result.stderr}")
        # Try re-encoding instead
        cmd2 = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", filelist_path, "-acodec", "libmp3lame", "-q:a", "2", output_temp
        ]
        result = subprocess.run(cmd2, capture_output=True, text=True)
        if result.returncode != 0:
            log(f"ffmpeg re-encode also failed: {result.stderr}")
            sys.exit(1)

    final_size = os.path.getsize(output_temp)
    log(f"Final audio: {output_temp} ({final_size} bytes)")

    # Step 7: Copy to output paths
    for outpath in OUTPUT_PATHS:
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        subprocess.run(["cp", output_temp, outpath], check=True)
        log(f"Copied to {outpath}")

    log("=== TTS Audio Assembly Complete! ===")
    log(f"Audio files at:")
    for p in OUTPUT_PATHS:
        log(f"  {p} ({os.path.getsize(p)} bytes)")

    # Write completion marker
    with open(os.path.join(WORK_DIR, "DONE"), 'w') as f:
        f.write(f"Completed at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Chunks: {len(chunk_files)}\n")
        f.write(f"Final size: {final_size}\n")
        for p in OUTPUT_PATHS:
            f.write(f"Output: {p}\n")

if __name__ == "__main__":
    main()
