#!/usr/bin/env python3
"""
Concurrent Load Test: /investment-opportunity/ Chat API
5 simultaneous sessions, each with different investor codes.
Tests: response time, identity leaks, cross-contamination, quality.
"""

import asyncio
import aiohttp
import time
import json
import os
from datetime import datetime

API_URL = "https://chy-jared.app.purebrain.ai/api/investment-chat"

async def run_session(session_name, code, questions):
    results = []
    history = []
    async with aiohttp.ClientSession() as http:
        for q in questions:
            start = time.time()
            try:
                resp = await asyncio.wait_for(
                    http.post(API_URL, json={"message": q, "history": history, "code": code}),
                    timeout=30
                )
                data = await resp.json()
                elapsed = time.time() - start
                answer = data.get("response", data.get("message", str(data)))
                answer_preview = answer[:200] if answer else ""

                # Check quality
                has_identity_leak = any(w in answer.lower() for w in [
                    "i am claude", "i'm claude", "as an ai language model",
                    "as claude", "i am an ai language model"
                ])
                presents_as_chy = "chy" in answer.lower() or "pure" in answer.lower()

                results.append({
                    "question": q,
                    "time": round(elapsed, 2),
                    "status": resp.status,
                    "answer_preview": answer_preview,
                    "full_answer": answer or "",
                    "identity_leak": has_identity_leak,
                    "presents_as_chy": presents_as_chy
                })

                # Add to history for context
                history.append({"role": "user", "content": q})
                history.append({"role": "assistant", "content": answer_preview})

            except asyncio.TimeoutError:
                results.append({
                    "question": q, "time": 30, "status": "TIMEOUT",
                    "answer_preview": "", "full_answer": "",
                    "identity_leak": False, "presents_as_chy": False
                })
            except Exception as e:
                elapsed = time.time() - start
                results.append({
                    "question": q, "time": round(elapsed, 2),
                    "status": f"ERROR: {e}",
                    "answer_preview": "", "full_answer": "",
                    "identity_leak": False, "presents_as_chy": False
                })

    return session_name, code, results


async def main():
    sessions = [
        ("Session 1", "PUREBRAIN2026", [
            "What is Pure Technology?",
            "What's the revenue model?",
            "Who is on the team?"
        ]),
        ("Session 2", "AYTON2026", [
            "What's the competitive moat?",
            "How does PureBrain differ from ChatGPT?",
            "What's the MRR projection?",
            "When do you expect breakeven?"
        ]),
        ("Session 3", "BOUDREAU2026", [
            "Why should I invest now?",
            "What's the use of funds?",
            "Who are your current customers?"
        ]),
        ("Session 4", "HAMMERSCHMID2026", [
            "What's the total addressable market?",
            "How does the technology work?",
            "What are the risks?",
            "Who are the competitors?",
            "What's your unfair advantage?"
        ]),
        ("Session 5", "DONATO2026", [
            "Tell me about Jared Sanborn",
            "What's the valuation?",
            "How many paying customers do you have?",
            "What's the exit strategy?",
            "When was the company founded?",
            "What IP do you own?",
            "Who is Chy?"
        ]),
    ]

    print(f"Starting concurrent load test at {datetime.now().isoformat()}")
    print(f"API: {API_URL}")
    print(f"Sessions: {len(sessions)}")
    print(f"Total questions: {sum(len(s[2]) for s in sessions)}")
    print("=" * 60)

    start = time.time()
    tasks = [run_session(name, code, qs) for name, code, qs in sessions]
    results = await asyncio.gather(*tasks)
    total_time = time.time() - start

    # Cross-contamination check
    # Build per-session question sets for checking
    session_questions = {}
    for name, code, qs in sessions:
        session_questions[name] = set()
        for q in qs:
            # Extract key terms unique to each session's questions
            for word in q.lower().split():
                if len(word) > 5:
                    session_questions[name].add(word)

    # Check if any session's answers reference unique terms from other sessions' questions
    cross_contamination_found = []
    for name, code, session_results in results:
        for r in session_results:
            answer_lower = r["full_answer"].lower()
            for other_name, other_code, _ in sessions:
                if other_name == name:
                    continue
                # Check if the other session's code appears in this session's answer
                if other_code.lower() in answer_lower:
                    cross_contamination_found.append(
                        f"{name} answer contains {other_name}'s code ({other_code})"
                    )

    # Build report
    report_lines = []
    report_lines.append(f"# Investment Opportunity Chat API - Concurrent Load Test")
    report_lines.append(f"")
    report_lines.append(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**API Endpoint**: `{API_URL}`")
    report_lines.append(f"**Concurrent Sessions**: 5")
    report_lines.append(f"**Total Questions**: {sum(len(r[2]) for r in results)}")
    report_lines.append(f"**Total Wall Time**: {total_time:.1f}s")
    report_lines.append(f"")
    report_lines.append(f"---")
    report_lines.append(f"")

    # Summary table
    report_lines.append(f"## Summary Table")
    report_lines.append(f"")
    report_lines.append(f"| Session | Code | Questions | Avg Response Time | Timeouts | Identity Leaks | Cross-Contamination | Pass/Fail |")
    report_lines.append(f"|---------|------|-----------|-------------------|----------|----------------|-----------------------|-----------|")

    all_pass = True
    all_times = []
    total_timeouts = 0
    total_leaks = 0

    for name, code, session_results in results:
        times = [r["time"] for r in session_results if r["status"] != "TIMEOUT"]
        avg_time = sum(times) / len(times) if times else 0
        all_times.extend(times)
        timeouts = sum(1 for r in session_results if r["status"] == "TIMEOUT")
        total_timeouts += timeouts
        leaks = sum(1 for r in session_results if r["identity_leak"])
        total_leaks += leaks
        n_questions = len(session_results)

        # Cross-contamination for this session
        cc = any(name in c for c in cross_contamination_found)

        session_pass = all(
            (r["status"] == 200 or r["status"] == "TIMEOUT") and not r["identity_leak"]
            for r in session_results
        ) and not cc and timeouts == 0

        if not session_pass:
            all_pass = False

        report_lines.append(
            f"| {name} | {code} | {n_questions} | {avg_time:.2f}s | {timeouts} | {leaks} | {'YES' if cc else 'None'} | {'PASS' if session_pass else 'FAIL'} |"
        )

    report_lines.append(f"")

    # Overall stats
    overall_avg = sum(all_times) / len(all_times) if all_times else 0
    report_lines.append(f"## Overall Statistics")
    report_lines.append(f"")
    report_lines.append(f"- **Average response time**: {overall_avg:.2f}s")
    report_lines.append(f"- **Min response time**: {min(all_times):.2f}s" if all_times else "- **Min response time**: N/A")
    report_lines.append(f"- **Max response time**: {max(all_times):.2f}s" if all_times else "- **Max response time**: N/A")
    report_lines.append(f"- **Total timeouts**: {total_timeouts}")
    report_lines.append(f"- **Total identity leaks**: {total_leaks}")
    report_lines.append(f"- **Cross-contamination incidents**: {len(cross_contamination_found)}")
    report_lines.append(f"- **Overall result**: **{'ALL PASS' if all_pass else 'FAILURES DETECTED'}**")
    report_lines.append(f"")
    report_lines.append(f"---")
    report_lines.append(f"")

    # Detailed results
    report_lines.append(f"## Detailed Results")
    report_lines.append(f"")

    for name, code, session_results in results:
        report_lines.append(f"### {name} ({code})")
        report_lines.append(f"")

        for r in session_results:
            status_str = r["status"]
            if status_str == 200:
                status_str = "200 OK"
            leak_flag = " -- IDENTITY LEAK" if r.get("identity_leak") else ""
            chy_flag = " (presents as Chy/Pure)" if r.get("presents_as_chy") else " (NO Chy/Pure reference)"

            report_lines.append(f"**Q**: {r['question']}")
            report_lines.append(f"**A**: {r['answer_preview'][:150]}{'...' if len(r.get('answer_preview','')) > 150 else ''}")
            report_lines.append(f"**Time**: {r['time']}s | **Status**: {status_str}{leak_flag}{chy_flag}")
            report_lines.append(f"")

    # Cross-contamination details
    report_lines.append(f"---")
    report_lines.append(f"")
    report_lines.append(f"## Cross-Contamination Analysis")
    report_lines.append(f"")
    if cross_contamination_found:
        for c in cross_contamination_found:
            report_lines.append(f"- {c}")
    else:
        report_lines.append(f"No cross-contamination detected. Each session's answers stayed independent of other sessions' investor codes.")
    report_lines.append(f"")

    # Write report
    report = "\n".join(report_lines)
    output_path = "/home/jared/exports/portal-files/investment-opportunity-load-test.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    # Print to console too
    print(report)

    # Print JSON summary for machine parsing
    summary = {
        "total_time": round(total_time, 1),
        "total_questions": sum(len(r[2]) for r in results),
        "avg_response_time": round(overall_avg, 2),
        "timeouts": total_timeouts,
        "identity_leaks": total_leaks,
        "cross_contamination": len(cross_contamination_found),
        "overall_pass": all_pass
    }
    print(f"\n--- JSON SUMMARY ---")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
