#!/usr/bin/env bash
# transcode.sh — Convert MP4 to HLS (master.m3u8 + .ts segments)
# Usage: transcode.sh <input.mp4> <output_dir>
#
# Creates:
#   output_dir/master.m3u8    — HLS playlist
#   output_dir/seg_NNN.ts     — 10-second segments
#
# Encoding: H.264 (copy if already H.264, re-encode if not)
# Audio: AAC 128k

set -euo pipefail

INPUT="$1"
OUTPUT_DIR="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "Usage: $0 <input.mp4> <output_dir>"
  exit 1
fi

if [ ! -f "$INPUT" ]; then
  echo "ERROR: Input file not found: $INPUT"
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "[transcode] Input: $INPUT"
echo "[transcode] Output: $OUTPUT_DIR"
echo "[transcode] Starting HLS transcode..."

# Check if video is already H.264
VCODEC=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of csv=p=0 "$INPUT" 2>/dev/null || echo "unknown")

if [ "$VCODEC" = "h264" ]; then
  echo "[transcode] Video is H.264 — using copy mode (fast)"
  VIDEO_OPTS="-c:v copy"
else
  echo "[transcode] Video is $VCODEC — re-encoding to H.264"
  VIDEO_OPTS="-c:v libx264 -preset fast -crf 23"
fi

ffmpeg -y -i "$INPUT" \
  $VIDEO_OPTS \
  -c:a aac -b:a 128k \
  -f hls \
  -hls_time 10 \
  -hls_list_size 0 \
  -hls_segment_filename "$OUTPUT_DIR/seg_%03d.ts" \
  -hls_playlist_type vod \
  "$OUTPUT_DIR/master.m3u8"

SEGMENTS=$(ls "$OUTPUT_DIR"/seg_*.ts 2>/dev/null | wc -l)
echo "[transcode] Complete. Segments: $SEGMENTS"
echo "[transcode] Playlist: $OUTPUT_DIR/master.m3u8"
ls -lh "$OUTPUT_DIR/master.m3u8"
