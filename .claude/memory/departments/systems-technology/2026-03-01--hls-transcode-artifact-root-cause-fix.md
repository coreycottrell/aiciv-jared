# HLS Transcode Artifact Root Cause and Fix

**Date**: 2026-03-01
**Type**: bug diagnosis + fix
**Component**: tools/video-pipeline/transcode.sh
**Symptom**: Gray/blank screen and green pixel artifacts at 4:01-4:25 in HLS stream
**Affected video**: c64e418d_purebrain-demo-video on R2 (master.m3u8)

---

## Root Cause: THREE Compounding Bugs

### Bug 1: Missing -sc_threshold 0

ffmpeg's scene change detector (default threshold=40) injects extra I-frames at
detected scene changes. This causes segment cuts at irregular points AND at
DIFFERENT timestamps per quality tier (because each resolution's encoder state
diverges). The 360p and 720p segment boundaries drifted apart by up to 10.03 seconds
by segment 021 of the video.

When HLS.js switches renditions (quality tiers), it seeks to the matching
segment NUMBER, not the matching TIMESTAMP. If segment 021 in 360p starts at
179.6s but segment 021 in 720p starts at 169.6s, the player jumps 10 seconds
backward in the stream. The decoder then tries to render a P-frame without its
reference I-frame = green screen.

### Bug 2: Missing -force_key_frames

Without -force_key_frames, the -hls_time flag is advisory only. ffmpeg cuts at
the next available keyframe AFTER HLS_SEGMENT_TIME seconds. With scene change
detection enabled, "next available keyframe" can be anywhere from 1-10 seconds.

### Bug 3: HLS_SEGMENT_TIME=2 was completely non-functional

The original 2s target was entirely ignored. Output TARGETDURATION was 10.
Segments ranged from 1.2s to 10.03s. The "2s" setting produced no 2-second
segments whatsoever.

---

## Proof: Segment Boundary Drift Analysis

Comparing 360p vs 720p cumulative segment start times before the fix:

| Segment | 360p starts at | 720p starts at | Drift |
|---------|---------------|----------------|-------|
| seg002  | 5.74s         | 7.47s          | 1.73s |
| seg009  | 63.09s        | 68.35s         | 5.26s |
| seg021  | 179.68s       | 169.65s        | 10.03s |

The drift grew continuously because each scene change created a differently
timed segment in each tier. By 3 minutes in, the tiers were a full 10 seconds
out of sync.

---

## Fix Applied

File: `/home/jared/projects/AI-CIV/aether/tools/video-pipeline/transcode.sh`
Backup: `transcode.sh.bak-2026-03-01-pre-artifact-fix`

Five changes made to the ffmpeg command in transcode_tier():

1. `-sc_threshold 0`
   Disables scene change I-frame injection. Segment cuts happen ONLY at
   the forced keyframe intervals, not at detected scene changes.

2. `-g ${GOP_SIZE}` (GOP_SIZE=180 for 30fps)
   Sets the GOP to exactly HLS_SEGMENT_TIME * FPS. Each segment contains
   exactly one complete GOP, starting and ending at an I-frame.

3. `-keyint_min ${GOP_SIZE}`
   Enforces minimum distance between keyframes = one full segment duration.
   Prevents ffmpeg from inserting unexpected early keyframes within a segment.

4. `-force_key_frames "expr:gte(t,n_forced*${HLS_SEGMENT_TIME})"`
   Guarantees an I-frame at EVERY segment boundary. The expr: form handles
   fractional FPS correctly (e.g. 29.97fps) unlike the simple time: form.
   This is the belt+suspenders guarantee on top of -g.

5. `-flags +cgop` (closed GOP)
   Each GOP is self-contained with no frame references crossing segment
   boundaries. Required for HLS compliance and random-access seeking.
   Without this, B-frames in one segment may reference frames in the
   previous segment, breaking seek operations.

6. `HLS_SEGMENT_TIME=6` (changed from 2)
   6s is the HLS VOD industry standard. 2s segments require an I-frame
   every 2 seconds which increases bitrate overhead. 6s gives the right
   balance of ABR switching speed and keyframe overhead.
   Also added `GOP_SIZE=180` constant (6s * 30fps).

---

## New Feature: verify_segment_alignment()

Added a post-transcode verification function that:
- Extracts cumulative segment start times from all tier playlists
- Compares them pairwise
- Reports max drift and segment count with >100ms drift
- FAILS with exit code 1 if max drift exceeds 500ms

This makes re-transcoding self-validating. If a future VFR source causes
drift, the pipeline catches it before upload to R2.

---

## VFR Source Warning

If the source video uses Variable Frame Rate (common with screen recordings
that drop frames during CPU-heavy moments), -sc_threshold 0 and -force_key_frames
together may still produce segments slightly longer than HLS_SEGMENT_TIME because
the frame at the forced timestamp may not exist.

Fix for VFR sources: pre-convert to CFR before transcoding:
  ffmpeg -i source.mp4 -vf fps=30 source_cfr.mp4

The script now logs a warning if TARGETDURATION exceeds HLS_SEGMENT_TIME+1.

---

## Re-transcode Required

The existing `c64e418d_purebrain-demo-video` on R2 was transcoded with the
broken script. It needs to be re-transcoded with the fixed script and re-uploaded.

DO NOT re-transcode until Jared confirms. The fix has been diagnosed and the
script corrected. The re-transcode step is next.

---

## Tags

hls, ffmpeg, artifacts, green-screen, transcode, ABR, GOP, keyframe, sc_threshold,
force_key_frames, cgop, segment-alignment, video-pipeline, r2, purebrain-demo-video
