#!/usr/bin/env python3
"""
Monitor Brainiac HLS transcoding and auto-upload to R2 when complete.
Checks every 60 seconds if ffmpeg is done, then uploads all segments.
"""

import os
import sys
import time
import subprocess
import boto3
from pathlib import Path

# R2 config
from dotenv import load_dotenv
load_dotenv('/home/jared/projects/AI-CIV/aether/.env')

R2_ACCESS_KEY = os.getenv('R2_ACCESS_KEY')
R2_SECRET_KEY = os.getenv('R2_SECRET_KEY')
R2_ENDPOINT = 'https://e42043210a9b4488a498a8be2c340742.r2.cloudflarestorage.com'
R2_BUCKET = 'purebrain-video'
R2_PUBLIC_URL = 'https://pub-5e73e235a2394ba3abf975138fdc5c7c.r2.dev'

# Telegram notification
def notify_telegram(msg):
    try:
        import json
        config = json.load(open('/home/jared/projects/AI-CIV/aether/config/telegram_config.json'))
        token = config['bot_token']
        subprocess.run([
            'curl', '-s', f'https://api.telegram.org/bot{token}/sendMessage',
            '-d', 'chat_id=548906264',
            '--data-urlencode', f'text={msg}'
        ], capture_output=True, timeout=10)
    except Exception as e:
        print(f"Telegram notify failed: {e}")

def upload_to_r2(local_dir, r2_prefix):
    """Upload all HLS files from local_dir to R2 under r2_prefix."""
    s3 = boto3.client('s3',
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name='auto'
    )

    files = sorted(Path(local_dir).glob('*'))
    total = len(files)
    uploaded = 0

    for f in files:
        if not f.is_file():
            continue
        key = f'{r2_prefix}/{f.name}'
        content_type = 'application/vnd.apple.mpegurl' if f.suffix == '.m3u8' else 'video/MP2T'

        print(f"  Uploading {f.name} ({f.stat().st_size / 1024:.0f} KB)...")
        s3.upload_file(
            str(f), R2_BUCKET, key,
            ExtraArgs={'ContentType': content_type}
        )
        uploaded += 1

        if uploaded % 50 == 0:
            print(f"  Progress: {uploaded}/{total} files uploaded")

    return uploaded

def is_ffmpeg_running_for(module_name):
    """Check if ffmpeg is still running for this module."""
    try:
        result = subprocess.run(
            ['pgrep', '-f', f'brainiac-hls/{module_name}'],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except:
        return False

def check_playlist_valid(hls_dir):
    """Check if master.m3u8 exists and has #EXT-X-ENDLIST (VOD complete)."""
    playlist = Path(hls_dir) / 'master.m3u8'
    if not playlist.exists():
        return False
    content = playlist.read_text()
    return '#EXT-X-ENDLIST' in content

def main():
    modules = {
        'module-1': {
            'hls_dir': '/tmp/brainiac-hls/module-1',
            'r2_prefix': 'brainiac/recordings/module-1',
            'expected_duration': '78 min',
            'done': False,
        },
        'module-2': {
            'hls_dir': '/tmp/brainiac-hls/module-2',
            'r2_prefix': 'brainiac/recordings/module-2',
            'expected_duration': '60 min',
            'done': False,
        },
    }

    print("Brainiac HLS Upload Monitor started")
    print(f"Monitoring: {', '.join(modules.keys())}")
    notify_telegram("Brainiac upload monitor started. Will auto-upload modules to R2 when transcoding completes.")

    while not all(m['done'] for m in modules.values()):
        for name, mod in modules.items():
            if mod['done']:
                continue

            ffmpeg_running = is_ffmpeg_running_for(name)
            segment_count = len(list(Path(mod['hls_dir']).glob('segment_*.ts'))) if Path(mod['hls_dir']).exists() else 0
            playlist_valid = check_playlist_valid(mod['hls_dir'])

            print(f"[{time.strftime('%H:%M:%S')}] {name}: ffmpeg={'running' if ffmpeg_running else 'DONE'}, segments={segment_count}, playlist={'valid' if playlist_valid else 'incomplete'}")

            if not ffmpeg_running and playlist_valid:
                print(f"\n{'='*60}")
                print(f"  {name} transcode COMPLETE! {segment_count} segments.")
                print(f"  Uploading to R2: {mod['r2_prefix']}")
                print(f"{'='*60}\n")

                notify_telegram(f"Brainiac {name} transcode complete! {segment_count} segments ({mod['expected_duration']}). Uploading to R2...")

                try:
                    uploaded = upload_to_r2(mod['hls_dir'], mod['r2_prefix'])
                    hls_url = f"{R2_PUBLIC_URL}/{mod['r2_prefix']}/master.m3u8"
                    print(f"  Upload complete! {uploaded} files → {hls_url}")
                    notify_telegram(f"Brainiac {name} uploaded to R2! {uploaded} files.\nHLS URL: {hls_url}")
                    mod['done'] = True
                except Exception as e:
                    print(f"  Upload FAILED: {e}")
                    notify_telegram(f"Brainiac {name} upload FAILED: {e}")

        if not all(m['done'] for m in modules.values()):
            time.sleep(60)

    print("\nAll modules uploaded successfully!")
    notify_telegram("All Brainiac modules uploaded to R2 successfully! Both Module 1 (78 min) and Module 2 (60 min) are live.")

if __name__ == '__main__':
    main()
