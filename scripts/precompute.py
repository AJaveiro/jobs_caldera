"""
precompute.py — PIECE 1: Build career text for each candidate
Run: python scripts/precompute.py

Today we ONLY build the career text and print it.
We are NOT embedding yet. We want to see exactly what text
we're about to feed into the AI model before we trust it.
"""

import json

DATA_PATH = "data/candidates.jsonl"


def build_career_text(candidate):
    """
    Combine headline + summary + every job description into
    one block of text. This is what we'll compare against the JD.
    """
    p = candidate["profile"]

    parts = []
    parts.append(p["headline"])
    parts.append(p["summary"])

    for job in candidate["career_history"]:
        # title + company gives context, description has the substance
        parts.append(f"{job['title']} at {job['company']}: {job['description']}")

    # Join everything with a space. This becomes one long string.
    return " ".join(parts)


def main():
    candidates = []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 5:   # just 5 for now — we're testing, not running for real
                break
            candidates.append(json.loads(line))

    print(f"Loaded {len(candidates)} candidates\n")

    for c in candidates:
        text = build_career_text(c)
        print("=" * 70)
        print(f"CANDIDATE: {c['candidate_id']} - {c['profile']['current_title']}")
        print("=" * 70)
        print(f"Career text length: {len(text)} characters")
        print(f"\nFirst 400 characters:\n{text[:400]}...")
        print()


if __name__ == "__main__":
    main()