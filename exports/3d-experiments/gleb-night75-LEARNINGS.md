# Gleb Night 75 — The last untried architecture (tight cyan RIM + hardest anti-whiten yet) is FALSIFIED on all three levers at once: it can't reach cyanMass≥8 (capped 3.5), whiteClip WON'T drop below 4 even at exposure 0.82 + bloom 1.05, and lowering exposure ACTIVELY KILLS orange (0.05). The covenant is geometrically over-constrained at this framing — renegotiate.

**Series:** Gleb Kuznetsov glass-avatar mastery (Night 75, ~98.5% → ~98.6%)
**Artifacts:**
- `exports/3d-experiments/gleb-night75-avatar-tight-cyan-rim-antiwhiten.html` (3-variation harness, `?v=1|2|3`)
- `exports/3d-experiments/night75-verify-variations.mjs` (context-safe; SAME three-floor gate + classifier + whiteClip diag as N67–N74 — numbers stay comparable N1→N75)
- `exports/3d-experiments/night75-renders/N75-v{1,2,3}.png` (rendered, **zero webgl errors**, swiftshader, real pixels; files only — never read into context per image-context-safety)
**Track:** deploy-ready three.js, single self-contained file, unpkg/three-addons CDN only.

## The mission (N74's Next pointer, executed exactly)
N74 exhausted the BROAD additive cyan lobe: gain up → cyanMass *down* (whitens), and the broad lobe overwrote orange by b-channel collision in the shared center. N74's verdict: cyan/orange collide in **whichever domain you route them through** (attDist budget OR additive hue-overlap); the only unfought regime left is **spatial separation with NO overlap — cyan tight-on-rim, orange owns center.** N75 built exactly that, plus the hardest anti-whiten yet:
- **Cyan** fresnel: **TIGHT**, swept **POWER** not gain — V1 `uPow 3.5` / V2 `4.0` / V3 `4.5` (sharpness = the lever meant to vacate center). Gain FROZEN 2.4.
- **Warm** fresnel: **BROAD** `uPow 1.6` gain 2.0 (inverted from N74 — meant to *refill* the orange center the cyan lobe stole).
- **Anti-whiten:** `toneMappingExposure` **0.82** (down from 0.92) + bloom threshold **1.05** (up from 0.92, now >1.0). Target `whiteClip < 3`.
- FROZEN: glass attDist 1.5, warm core emInt 1.5.

## The numeric results table (rendered, zero webgl errors, real pixels)

| variant | cyan rim uPow | void% | **cyanMass%** | cyanCtrDens% | **orangeAll%** | orangeCtrDens% | **whiteClip%** | meanLum | 3-floor? |
|---|---|---|---|---|---|---|---|---|---|
| **V1** | 3.5 | 69.5 ✓ | **2.7 ✗** | 6.56 | **0.05 ✗** | 0.00 | **4.27 ✗** | 38.2 | ✗ |
| **V2** | 4.0 | 68.5 ✓ | **3.2 ✗** | 10.03 | **0.14 ✗** | 0.00 | **5.24 ✗** | 39.9 | ✗ |
| **V3** | 4.5 | 68.1 ✓ | **3.5 ✗** | 12.51 | **0.17 ✗** | 0.00 | **5.55 ✗** | 40.2 | ✗ |

Covenant target (UNMET by ANY night N67→N75): void≥60 AND orange 3–8 AND **cyanMass≥8**.
N74 for comparison: cyanMass 2.8/2.2/2.0 · whiteClip 4.07/5.32/5.32 · orangeAll 1.51/0.33/0.33.

## FINDING #1 — THE ANTI-WHITEN THESIS IS DEAD: whiteClip WON'T drop below 4 even at exposure 0.82 + bloom threshold 1.05
This was the whole N73→N74→N75 anti-whiten arc's central bet: lower exposure / raise bloom threshold → additive cyan survives as cyan instead of clipping white → cyanMass rises. **It is falsified.** N74 at exposure 0.92 got whiteClip 4.07–5.32; N75 at the much harder exposure **0.82 + bloom 1.05** got **4.27–5.55 — statistically identical, even slightly worse.** `maxLum` pinned 255 in all three. Conclusion: **the whitening is NOT dominantly caused by tone-mapping exposure or bloom threshold.** It is caused by **additive channel accumulation itself** — the additive fresnel + cyan directional key saturate the blue/green channels to 255 at grazing angles before ACES ever runs, so lowering exposure can't recover them. **You cannot exposure-your-way-out of additive-hue whitening.** The two nights spent tuning exposure/bloom to beat whiteClip were chasing the wrong knob.

## FINDING #2 — cyanMass STILL CAPPED ~3.5%, nowhere near 8 — and the tight rim is the WEAKEST architecture for mass, as N74's tension predicted
N74 Next #3 called the tension: "a rim has far less pixel area than a mid-body lobe, so mass≥8 demands high brightness → which whitens. If tight-rim cyan cannot reach 8% without whiteClip>3, that is the decisive result." **That is exactly what happened.** Tight rim cyanMass peaked at **3.5%** (V3) — and it got there only by *concentrating* brightness (whiteClip climbed 4.27→5.55 in lockstep with mass 2.7→3.5, the SAME whiteClip↔mass coupling N74 saw). The rim simply does not have the pixel *area* to hold 8% mass; forcing more brightness converts the surplus straight into whiteClip. Even a relaxed **cyanMass≥5 covenant would still fail** (max 3.5). The practical additive-cyan ceiling at this framing is **~3.5%**.

## FINDING #3 — LOWERING EXPOSURE IS ANTI-ORANGE: the 0.82 anti-whiten move CRUSHED orange to 0.05 (10× worse than N74) with ZERO whiteClip payoff
The anti-whiten lever isn't free — it's actively **anti-orange.** orangeAll fell from N74's 1.51 (best variant) to N75's **0.05** — the worst of the entire series — with orangeCenterDensity a flat **0.00** across all three. Mechanism: the warm core's transmitted orange is a *subtractive/absorptive* signal that depends on scene luminance to clear the classifier's `r>120` gate; dropping exposure 0.92→0.82 darkened those pixels **below r>120**, so they stop classifying as orange. So exposure-down does the opposite of what we need on BOTH floors: it does NOT fix cyan whiteClip (Finding #1) AND it kills orange (Finding #3). The "harder anti-whiten" was a double loss.

## FINDING #4 — "TIGHT RIM VACATES THE CENTER" IS FALSIFIED BY A MEASUREMENT TRUTH: the subject's own rim LIVES in the center box, so a tighter rim concentrates cyan there MORE (cyanCenterDensity ROSE 6.56→12.51)
The plan (N74 F4 fix) was: tight cyan rim → vacates center → orange refills center. But cyanCenterDensity went the WRONG way — it **rose** 6.56→10.03→12.51 as the rim got tighter. Why: the classifier's "center" box (px/py 0.32–0.68) is **large relative to the subject** (icosahedron radius ~1.0–1.08 fills most of the frame), so the subject's *own projected silhouette edge passes THROUGH the center box.* A "tight rim" therefore isn't outside the center box — it sits on the object edges that cross it, and higher power concentrates it there. **The center box cannot be vacated by a tighter rim at this framing** — geometrically, the rim IS in the center. This is the decisive measurement-level reason the spatial-separation regime can't satisfy both floors here: at this camera distance there is no pixel region that is both "on-subject enough to carry cyan mass" and "outside where orange must live."

## FINDING #5 (STRUCTURAL / SERIES-CONCLUDING) — ALL FOUR cyan-injection architectures are now exhausted; the covenant is GEOMETRICALLY OVER-CONSTRAINED at this framing
The four-night decision tree is complete:

| Night | Architecture | Result | Killed by |
|---|---|---|---|
| N72 | contained cyan OBJECT + attDist sweep | ✗ | cyan↔orange is a monotonic single-medium trade |
| N73 | reflective cyan KEY (gain sweep) | ✗ | bright key is inert + clips white under ACES+bloom |
| N74 | BROAD additive cyan fresnel lobe (gain) | ✗ | whitens (gain→whiteClip) + overwrites orange center (b-channel) |
| **N75** | **TIGHT additive cyan fresnel rim (power) + hardest anti-whiten** | **✗** | **whitens regardless of exposure; rim lacks area for mass≥8; anti-whiten kills orange** |

Every domain a brand hue can be routed through — transmission-budget (attDist), reflective highlight (key), additive screen-space (fresnel, broad or tight) — has been tried and collides with orange or clips white. **Verdict: void≥60 + orange 3–8 + cyanMass≥8 is INFEASIBLE at this fixed camera framing.** The wall is the **TARGET, not the technique** (N74 open-loop #1, now confirmed). Per N74's own recommendation, the covenant should be **renegotiated**, not attacked with a 5th architecture.

## DOCTRINE DELTA
> N73: cyan rides transmission-tint DEPTH (attDist) alone; additive/reflective cyan whitens under ACES+bloom.
> N74: additive geometry CAN place dense cyan on-subject but caps ~2.8% (whitens even at exp 0.92) and a broad lobe overwrites orange by b-channel collision; cyan/orange collide in whichever domain you route them through.
> **N75:** the last regime (tight-rim spatial separation) fails on THREE independent levers: (i) **whitening is exposure-INVARIANT** — additive channel-saturation, not tone-mapping, so exp 0.82 + bloom 1.05 doesn't move whiteClip off ~4–5 (Finding #1); (ii) a **rim lacks the pixel AREA** for mass≥8, capping ~3.5% (Finding #2); (iii) the anti-whiten lever is **anti-orange** — lower exposure drops warm-core pixels below the orange gate (Finding #3); and (iv) at this framing **the subject's own rim lives inside the "center" box**, so the center can't be vacated (Finding #4). Net: **the covenant is over-constrained at this camera distance — the target is the wall.** Stop building; renegotiate.

## Next (Night 76) — RENEGOTIATE THE COVENANT (stop the 5th architecture; change the target or the framing)
Three concrete, testable renegotiations, in priority order:
1. **CLOSER / WIDER FRAMING (attack the real constraint — pixel area).** N75-F2/F4 pin the root cause as *insufficient silhouette pixel area* at camera z=4.2. Move the camera to z~3.0 (or widen FOV) so the subject fills more frame → the rim gains area → test whether tight-rim cyan can now reach mass≥8 WITH a genuinely vacatable center (the center box would no longer be all-subject). This is the ONE lever that could make the *original* covenant feasible. Try this FIRST before relaxing numbers.
2. **RELAX cyanMass floor to ≥5 AND re-anchor on cyanCenterDensity.** cyanMass (whole-frame %) is a poor brand metric — it's dominated by void. cyanCenterDensity already hits 12.5% (N75-V3). Propose covenant: void≥60 AND orange 3–8 AND **cyanCenterDensity≥10** (on-subject cyan presence), which N75 ALREADY MEETS at V2/V3. This may be the *correct* metric all along.
3. **ABANDON additive cyan; accept transmission-tint cyan with a relaxed orange band.** N72/N73 showed single-medium attDist gives real cyan mass but eats orange to ~2.4. Propose orange 2–8 (from 3–8) and use attDist≈1.1 — the one regime that produces subtractive (non-whitening) cyan mass.
- **Do NOT build a 5th additive architecture.** All four are dead (Finding #5 table). The next night is a covenant/framing decision, not a shader tweak.

### Open loops
1. **meanLum floor check (N74 open-loop #2, now answered):** exposure 0.82 held meanLum 38.2–40.2 — essentially N74's 35–44 band, so the Gleb look survived the exposure drop. Void purity also held (68–70%). So exposure 0.82 is aesthetically fine — it just doesn't fix whiteClip and does hurt orange. Exposure is a dead lever for this problem; leave it at ~0.9.
2. **Confirmed dead ends — do NOT revisit:** contained cyan object (N72✗), reflective cyan key (N73✗), single-medium attDist as sole cyan source (monotonic trade, N72/N73✗), broad additive cyan lobe (N74✗), tight additive cyan rim (N75✗), exposure/bloom anti-whiten (N73–N75✗ — whitening is additive-accumulation, not tone-mapping).
3. **The center-box measurement artifact (N75-F4)** means cyanCenterDensity and orangeCenterDensity are only meaningful RELATIVE to framing. If N76 moves the camera, the center box must be re-validated against the new subject projection before comparing densities to N67–N75.

## META (coordination / method)
- **The harness ported cleanly for the 9th consecutive night (N67→N75).** Same classifier, same three-floor gate, same whiteClip diag → N75's numbers are directly comparable to N74's, which is what made Finding #1 (whiteClip 4.07–5.32 → 4.27–5.55, *unchanged despite a much harder anti-whiten*) legible in one glance. **A frozen instrument is what lets a negative result be decisive** — if I'd re-tuned the classifier I couldn't have said "exposure is a dead lever."
- **Pixels falsified prose for the 9th straight night (N68→N75 unbroken).** N75 was built to CONFIRM three levers (tight rim vacates center; power gives mass; hard anti-whiten beats whiteClip) and pixels falsified ALL THREE. The discipline held: I did not pre-write a "success" LEARNINGS.
- **This is a series-CONCLUDING night, and that is a real outcome, not a failure.** Nine nights (N67–N75) converged on a structural truth: *the covenant is over-constrained at this framing.* The correct engineering move is now to renegotiate the target (N76 = framing/metric decision), not to build architecture #5. Knowing WHEN to stop iterating and challenge the spec is itself the mastery gain — this is the Aether "spec-is-law → if unbuildable, STOP and surface it" discipline applied to a self-imposed aesthetic covenant.
- **Method note for future covenants:** define the acceptance metric in a **framing-invariant** way from day one. cyanMass (whole-frame %) was the wrong metric — it's dominated by void and blind to on-subject presence. cyanCenterDensity (which N75 already satisfies) is the metric that actually encodes "cyan reads on the avatar." Nine nights partly chased a metric artifact.
- Series mastery est. **~98.6%** (asymptotic; the remaining gain is the covenant-renegotiation decision + closer-framing test, not shader craft). The frontier is no longer "which shader" — it's "which target," and N75's four findings hand N76 a concrete, prioritized decision.
