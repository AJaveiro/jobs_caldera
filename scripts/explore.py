'''import json
import sys
from pprint import pprint

sys.stdout.reconfigure(encoding="utf-8")

with open("data/candidates.jsonl", "r", encoding="utf-8") as f:
    for i, line in enumerate(f,start=1):
        candidate = json.loads(line)
        
        print("\n"+"="*80)
        print(f"CANDIDATE # {i}")
        print("="*80)
        pprint(candidate)
        if i >= 10:
            break
    '''
    
"""
explore.py — Read and understand candidate profiles
Run: python scripts/explore.py
Controls: Enter = next candidate, q = quit, number = jump to that candidate
"""

import json
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

DATA_PATH = "data/candidates.jsonl"
TODAY = date(2026, 6, 16)


# ── Helpers ───────────────────────────────────────────────────────────────────

def days_since(date_str):
    d = date.fromisoformat(date_str)
    return (TODAY - d).days

def bar(value, width=20):
    """Visual bar for 0-1 values."""
    filled = int(value * width)
    return "█" * filled + "░" * (width - filled)

def signal_label(value, thresholds, labels):
    """Convert a value to a human label based on thresholds."""
    for threshold, label in zip(thresholds, labels):
        if value <= threshold:
            return label
    return labels[-1]

CONSULTING_FIRMS = {
    "tcs", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "hcl", "tech mahindra", "mindtree", "mphasis",
    "hexaware", "ltimindtree", "persistent"
}

def is_consulting(company_name):
    return any(firm in company_name.lower() for firm in CONSULTING_FIRMS)


# ── Printing ──────────────────────────────────────────────────────────────────

def print_candidate(c, index):
    p  = c["profile"]
    s  = c["redrob_signals"]

    print("\n" + "═" * 65)
    print(f"  CANDIDATE #{index + 1}  —  {c['candidate_id']}")
    print("═" * 65)

    # ── Profile ──────────────────────────────────────────────────────────────
    print(f"\n  {p['current_title']}")
    print(f"  {p['current_company']}  ({p['current_company_size']} employees)")
    print(f"  {p['location']}, {p['country']}  |  {p['years_of_experience']} yrs exp")
    print(f"  Industry: {p['current_industry']}")

    if is_consulting(p["current_company"]):
        print(f"  ⚠  Consulting firm detected — JD says not preferred")

    print(f"\n  Headline: {p['headline']}")
    print(f"\n  Summary:\n  {p['summary'][:300]}{'...' if len(p['summary']) > 300 else ''}")

    # ── Career ───────────────────────────────────────────────────────────────
    print(f"\n{'─' * 65}")
    print(f"  CAREER HISTORY ({len(c['career_history'])} roles)")
    print(f"{'─' * 65}")

    for job in c["career_history"]:
        current_tag = " ← current" if job["is_current"] else ""
        consulting_tag = " ⚠ consulting" if is_consulting(job["company"]) else ""
        yrs = job["duration_months"] / 12
        print(f"\n  {job['title']}")
        print(f"  {job['company']}  |  {yrs:.1f} yrs{current_tag}{consulting_tag}")
        print(f"  {job['start_date']}  →  {job['end_date'] or 'present'}")
        # Show first 180 chars of description so you can see what they actually did
        desc = job["description"][:180].replace("\n", " ")
        print(f"  \"{desc}...\"")

    # ── Skills ───────────────────────────────────────────────────────────────
    print(f"\n{'─' * 65}")
    print(f"  SKILLS ({len(c['skills'])} total)")
    print(f"{'─' * 65}")

    # Separate skills with real usage vs suspicious ones
    real_skills     = [sk for sk in c["skills"] if sk.get("duration_months", 0) >= 6]
    suspect_skills  = [sk for sk in c["skills"] if sk.get("duration_months", 0) < 6]

    if real_skills:
        print(f"\n  Verified (6+ months use):")
        for sk in sorted(real_skills, key=lambda x: -x.get("duration_months", 0))[:8]:
            months = sk.get("duration_months", 0)
            print(f"    {sk['name']:<28} {sk['proficiency']:<14} {months} months")

    if suspect_skills:
        print(f"\n  ⚠  Low duration (<6 months — treat with caution):")
        for sk in suspect_skills[:5]:
            months = sk.get("duration_months", 0)
            print(f"    {sk['name']:<28} {sk['proficiency']:<14} {months} months")

    # Skill assessment scores if any
    assessments = s.get("skill_assessment_scores", {})
    if assessments:
        print(f"\n  Platform assessment scores:")
        for skill, score in list(assessments.items())[:5]:
            print(f"    {skill:<28} {score:.0f}/100  {bar(score/100, 12)}")

    # ── Education ────────────────────────────────────────────────────────────
    if c["education"]:
        print(f"\n{'─' * 65}")
        print(f"  EDUCATION")
        print(f"{'─' * 65}")
        for edu in c["education"]:
            tier = edu.get("tier", "unknown")
            grade = edu.get("grade") or "—"
            print(f"\n  {edu['degree']} in {edu['field_of_study']}")
            print(f"  {edu['institution']}  |  {edu['start_year']}–{edu['end_year']}  |  {tier}  |  {grade}")

    # ── Behavioral signals ───────────────────────────────────────────────────
    print(f"\n{'─' * 65}")
    print(f"  BEHAVIORAL SIGNALS")
    print(f"{'─' * 65}")

    days_inactive = days_since(s["last_active_date"])
    active_label  = signal_label(
        days_inactive,
        [7,   30,   90,   180],
        ["🟢 very recent", "🟢 recent", "🟡 moderate", "🔴 stale", "🔴 very stale"]
    )

    rr = s["recruiter_response_rate"]
    rr_label = signal_label(
        rr,
        [0.2, 0.5, 0.75],
        ["🔴 ghost", "🟡 low", "🟢 good", "🟢 great"]
    )

    notice = s["notice_period_days"]
    notice_label = signal_label(
        notice,
        [30, 60, 90],
        ["🟢 fast", "🟡 ok", "🟡 slow", "🔴 long"]
    )

    otw  = "🟢 Yes" if s["open_to_work_flag"] else "🔴 No"
    rel  = "🟢 Yes" if s["willing_to_relocate"] else "🔴 No"
    gh   = s["github_activity_score"]
    gh_s = f"{gh:.0f}/100" if gh >= 0 else "not linked"

    sal  = s["expected_salary_range_inr_lpa"]

    print(f"\n  Last active:         {s['last_active_date']}  ({days_inactive}d ago)  {active_label}")
    print(f"  Open to work:        {otw}")
    print(f"  Response rate:       {rr:.0%}  {bar(rr, 15)}  {rr_label}")
    print(f"  Avg response time:   {s['avg_response_time_hours']:.1f} hours")
    print(f"  Notice period:       {notice} days  {notice_label}")
    print(f"  Willing to relocate: {rel}")
    print(f"  Preferred work mode: {s['preferred_work_mode']}")
    print(f"  Salary expectation:  ₹{sal['min']}–{sal['max']} LPA")
    print(f"  GitHub activity:     {gh_s}")
    print(f"  Interview completion:{s['interview_completion_rate']:.0%}")
    print(f"  Offer acceptance:    {s['offer_acceptance_rate'] if s['offer_acceptance_rate'] >= 0 else 'no history'}")
    print(f"  Profile completeness:{s['profile_completeness_score']:.0f}%")
    print(f"  Saved by recruiters: {s['saved_by_recruiters_30d']} (last 30d)")

    # ── Your verdict ─────────────────────────────────────────────────────────
    print(f"\n{'─' * 65}")
    print(f"  YOUR VERDICT (write it down)")
    print(f"{'─' * 65}")
    print(f"  Shortlist?   YES  /  MAYBE  /  NO")
    print(f"  Why: _______________________________________________")
    print(f"  Strongest signal for:  _____________________________")
    print(f"  Biggest red flag:      _____________________________")


# ── Main loop ─────────────────────────────────────────────────────────────────

def main():
    print("\n  Loading candidates...")

    candidates = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            '''if i >= 50:   # load first 50 (the sample set)
                break'''
            candidates.append(json.loads(line))

    print(f"  Loaded {len(candidates)} candidates from {DATA_PATH}")
    print(f"  Controls: Enter = next  |  q = quit  |  type a number to jump\n")

    index = 0
    while 0 <= index < len(candidates):
        print_candidate(candidates[index], index)

        user = input(f"\n  [{index + 1}/{len(candidates)}]  Enter / number / q  → ").strip().lower()

        if user == "q":
            print("\n  Done.\n")
            break
        elif user.isdigit():
            jump = int(user) - 1
            if 0 <= jump < len(candidates):
                index = jump
            else:
                print(f"  Out of range. Pick 1–{len(candidates)}.")
        else:
            index += 1

    if index >= len(candidates):
        print("\n  Reached end of sample. Great job exploring!\n")


if __name__ == "__main__":
    main()