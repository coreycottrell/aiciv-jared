# Meshy API: Preview -> Refinement Workflow

**Date**: 2026-02-21
**Type**: teaching
**Topic**: Meshy two-stage generation workflow and quality expectations

---

## Memory Search Results
- Searched: Previous Meshy API learnings from Night 1 sprint
- Found: task 019c7da3 submitted as preview, confirmed mode="preview" in memory
- Applied: Refinement workflow as described in gotcha #5 from night 1

---

## Workflow Confirmed

### Stage 1: Preview Generation
- Task: 019c7da3-4700-77a3-88f2-96720c182a66
- Mode: text-to-3d-preview
- Status: SUCCEEDED (100%)
- Time to complete: ~3 minutes (started/finished timestamps from API)
- GLB size: 668KB - excellent for web
- Preview image: plain grey matte sphere (this is NORMAL - Meshy's default renderer)

### Stage 2: Refinement
- Task: 019c7e93-2a34-714f-9c2d-5dde2eadbc96
- Mode: refine
- Parent: preview task 019c7da3
- texture_richness: "high"
- Status at submission: IN_PROGRESS at 5%
- Expected time: 5-10 minutes additional

### API Call Pattern (Refinement)
```bash
curl -s -X POST "https://api.meshy.ai/v2/text-to-3d" \
  -H "Authorization: Bearer $MESHY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "refine",
    "preview_task_id": "PREVIEW_TASK_ID_HERE",
    "texture_richness": "high",
    "texture_prompt": "optional extra texture instructions"
  }'
```

---

## Key Insight: Meshy Generates Geometry, NOT Materials

The preview image shows a plain grey sphere. This is expected.

**Meshy's job**: Create clean, smooth geometry with proper UV mapping
**Your job**: Apply MeshTransmissionMaterial, HDRI, postprocessing in Three.js

Never judge a Meshy result by its preview thumbnail color. Judge it by:
1. Silhouette smoothness (no jagged edges)
2. UV mapping quality (affects how textures apply)
3. Polygon density (high = good for transmission materials)
4. File size appropriateness (668KB for web = ideal)

---

## File Paths
- Preview GLB: exports/3d-models/glass-orb-019c7da3.glb
- Preview thumbnail: exports/3d-models/glass-orb-019c7da3-preview.png
- Refinement task ID: 019c7e93-2a34-714f-9c2d-5dde2eadbc96
- Refinement GLB: TBD (download when SUCCEEDED)

---

## Next Steps After Refinement Completes
1. Check status: curl api.meshy.ai/v2/text-to-3d/019c7e93...
2. Download refined GLB
3. Load both versions in Three.js scene with MeshTransmissionMaterial
4. Compare: refined version should have better UV seams and texture baking
5. Decision: use preview or refined for the actual R3F component
