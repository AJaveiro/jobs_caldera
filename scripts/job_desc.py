print("JOB_DESC FILE STARTED")

"""
job_desc.py — Parse and extract structured requirements from the Job Description
Run: python scripts/job_desc.py

Outputs:
  - Prints a clean summary of everything extracted
  - Saves jd_parsed.json for use by rank.py later

This file is the single source of truth for what we're ranking against.
"""

import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_PATH = "outputs/jd_parsed.json"


# ─────────────────────────────────────────────────────────────────────────────
# THE JD — structured by hand from job_description.md
# We parse this manually (not with regex) because the JD is one document
# and we want full control over what each field means for our scorer.
# ─────────────────────────────────────────────────────────────────────────────

JD = {

    # ── Basic info ────────────────────────────────────────────────────────────
    "role_title": "Senior AI Engineer",
    "company": "Redrob AI",
    "employment_type": "Full-time",
    "stage": "Series A",  # important — startup pace, not FAANG

    # ── Experience ────────────────────────────────────────────────────────────
    "experience": {
        "preferred_years_min": 5,
        "preferred_years_max": 9,
        "note": "Range is a guideline not a hard cutoff. 4yr with strong signals OK. 15yr title-chaser not OK.",
        "sweet_spot": "6–8 years total, of which 4–5 in applied ML/AI at product companies"
    },

    # ── Location ──────────────────────────────────────────────────────────────
    "location": {
    "primary": ["Pune", "Noida"],
    "acceptable": ["Hyderabad", "Mumbai", "Delhi NCR"],
    "tier1_flexible": ["Bangalore", "Chennai"],
    "relocation_preferred": ["Pune", "Noida"],
    "outside_india": "case-by-case, no visa sponsorship",
    "work_mode": "Hybrid — flexible cadence, mostly Tue/Thu in office",
    "quarterly_travel": True
},

    # ── Notice period ─────────────────────────────────────────────────────────
    "notice_period": {
        "preferred_days": 30,
        "buyout_available_days": 30,
        "note": "30+ day candidates still in scope but bar is higher"
    },

    # ── Salary ────────────────────────────────────────────────────────────────
    "salary_lpa": {
        "realistic_min": 30,
        "realistic_max": 60,
        "note": "Series A AI startup — competitive but not FAANG. Below 20 = junior signal. Above 80 = likely won't accept."
    },

    # ── Must-have skills (hard requirements) ─────────────────────────────────
    "must_have_skills": [
        "embeddings-based retrieval",
        "vector databases",
        "semantic search",
        "hybrid search",
        "Python",
        "ranking system evaluation",
        "NDCG",
        "MRR",
        "MAP",
        "production ML deployment",
        "retrieval quality regression handling",
        "embedding drift handling"
    ],

    # ── Specific tools — any one of these per category is enough ─────────────
    "must_have_tools": {
        "embedding_models": [
            "sentence-transformers", "openai embeddings", "bge", "e5"
        ],
        "vector_dbs": [
            "pinecone", "weaviate", "qdrant", "milvus",
            "opensearch", "elasticsearch", "faiss"
        ]
    },

    # ── Nice-to-have skills (bonus, not required) ────────────────────────────
    "nice_to_have_skills": [
        "LLM fine-tuning",
        "LoRA",
        "QLoRA",
        "PEFT",
        "learning-to-rank",
        "XGBoost ranking",
        "neural ranking",
        "HR tech",
        "recruiting tech",
        "marketplace products",
        "distributed systems",
        "large-scale inference optimization",
        "open-source contributions"
    ],

    # ── What they'll actually do ──────────────────────────────────────────────
    "responsibilities": [
        "Own the intelligence layer — ranking, retrieval, matching systems",
        "Audit existing BM25 + rule-based system and identify high-leverage improvements",
        "Ship v2 ranking system with embeddings and hybrid retrieval within 8 weeks",
        "Set up evaluation infrastructure — offline benchmarks, A/B testing, feedback loops",
        "Drive long-term candidate-JD matching architecture at scale",
        "Mentor next round of hires (team growing from 4 to 12)",
        "Work closely with recruiter-experience PM on product direction"
    ],

    # ── What the JD actually means (read between the lines) ──────────────────
    "implicit_requirements": [
        "Has shipped at least one end-to-end ranking / search / recommendation system to real users",
        "Strong opinions on retrieval (hybrid vs dense) backed by real systems built",
        "Strong opinions on evaluation (offline vs online) backed by real experience",
        "Comfortable writing code — not just designing architecture",
        "Writes clearly — company is async-first and writing-heavy",
        "Can work scrappy — will ship a working ranker in a week even if suboptimal",
        "Has pre-LLM ML experience — not just LangChain wrappers post-2022"
    ],


    "culture_signals": [
        "async-first work style",
        "writes clearly",
        "comfortable with ambiguity",
        "open disagreement",
        "fast decision-making",
        "product thinking",
        "recruiter workflow understanding",
        "comfortable with unstable early-stage startup environment"
    ],

    "domain_context": [
        "recruiter search",
        "candidate discovery",
        "candidate-JD matching",
        "recruiter engagement metrics",
        "recruiter feedback loops",
        "talent intelligence platform"
    ],

    "ranking_guidance": [
        "Do not rank only by AI keyword count",
        "Career history matters more than skills list",
        "Product-company ranking/search/recommendation experience can beat keyword-heavy profiles",
        "Down-weight inactive candidates and low recruiter response rate",
        "A candidate with AI keywords but unrelated career history should not rank high",
        "Prefer 10 great matches over 1000 weak matches"
    ],
    # ── Red flags / explicit disqualifiers ───────────────────────────────────
    "red_flags": {

        "career_type": [
            "Entire career at consulting firms (TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini)",
            "Pure research roles only — academic labs, no production deployment ever",
            "Title-chaser — switching companies every 1.5 years chasing seniority"
        ],

        "skill_type": [
            "AI experience = only LangChain + OpenAI API calls in last 12 months with no prior ML",
            "Primary expertise in computer vision, speech, or robotics with no NLP/IR",
            "Has not written production code in last 18 months (pure architecture/tech lead)"
        ],

        "profile_type": [
            "5+ years on closed-source proprietary systems with no external validation",
            "Framework enthusiast — tutorials and demos, no systems thinking",
            "Marketing Manager / HR / Operations with AI keywords bolted onto skills"
        ],

        "consulting_firms": [
            "tcs", "infosys", "wipro", "accenture", "cognizant",
            "capgemini", "hcl", "tech mahindra", "mindtree", "mphasis"
        ]
    },

    # ── Behavioral signals the JD explicitly mentions ─────────────────────────
    "behavioral_requirements": [
        "Active on platform — logged in recently",
        "Responsive to recruiter messages",
        "In the job market — open to work or showing clear job-search signals"
    ],

    # ── Keywords for semantic matching ────────────────────────────────────────
    # These are the concepts the JD uses — our embedding of the JD text will
    # naturally capture these. Listed here for reference and for the skills scorer.
    "semantic_keywords": [
        "retrieval", "ranking", "matching", "embeddings", "vector search",
        "semantic search", "hybrid retrieval", "dense retrieval", "BM25",
        "recommendation system", "candidate ranking", "job matching",
        "NDCG", "MRR", "MAP", "evaluation framework", "A/B testing",
        "production deployment", "real users", "at scale",
        "sentence-transformers", "Pinecone", "Weaviate", "Qdrant", "Milvus",
        "FAISS", "Elasticsearch", "OpenSearch",
        "LLM", "fine-tuning", "LoRA", "RAG", "re-ranking",
        "Python", "ML systems", "inference", "embedding drift",
        "learning-to-rank", "XGBoost", "neural ranking","recruiter search",
        "candidate discovery","talent intelligence","recruiter engagement",
        "feedback loops","product company","shipper mindset","async writing"
    ],

    # ── The full JD text — used for embedding ─────────────────────────────────
    # This is what we embed and compare against every candidate's career text.
    # We use the core technical + responsibility sections only — not the culture
    # section, which would add noise to the semantic match.
    "jd_text_for_embedding": """
Senior AI Engineer at Redrob AI. Series A AI-native talent intelligence platform.
Location: Pune or Noida India, hybrid. Open to Hyderabad, Mumbai, Delhi NCR, Bangalore.
Experience: 5 to 9 years, ideal 6 to 8 years in applied ML and AI at product companies.

Role: Own the intelligence layer of Redrob — the ranking, retrieval, and matching systems
that decide what recruiters see when searching for candidates and what candidates see when
searching for roles. Ship a v2 ranking system with embeddings and hybrid retrieval.
Build evaluation infrastructure with offline benchmarks, A/B testing, and feedback loops.
Drive candidate to job description matching at scale. Mentor junior engineers.

Must have: Production experience with embeddings-based retrieval systems using
sentence-transformers, OpenAI embeddings, BGE, E5 or similar, deployed to real users.
Handled embedding drift, index refresh, and retrieval quality regression in production.
Production experience with vector databases or hybrid search infrastructure such as
Pinecone, Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS.
Strong Python. Experience designing evaluation frameworks for ranking systems including
NDCG, MRR, MAP, offline to online correlation, and A/B test interpretation.

Nice to have: LLM fine-tuning with LoRA QLoRA PEFT. Learning to rank with XGBoost
or neural models. HR tech or recruiting tech experience. Distributed systems.
Large scale inference optimization. Open source contributions in AI ML.

Ideal candidate: Has shipped at least one end-to-end ranking search or recommendation
system to real users at meaningful scale. Strong opinions on retrieval hybrid versus dense,
evaluation offline versus online, and LLM integration when to fine-tune versus prompt.
Can ship a working system in a week. Writes production code. Pre-LLM ML experience.
Not just LangChain wrappers. Systems thinker not framework enthusiast.
""".strip()
}


# ─────────────────────────────────────────────────────────────────────────────
# Print summary
# ─────────────────────────────────────────────────────────────────────────────

def print_jd_summary():
    print("\n" + "═" * 70)
    print("  JD PARSED SUMMARY")
    print("═" * 70)

    print(f"\n  Role:      {JD['role_title']} — {JD['company']} ({JD['stage']})")
    print(f"  Type:      {JD['employment_type']}")

    exp = JD["experience"]
    print(f"\n  Experience: {exp['preferred_years_min']}–{exp['preferred_years_max']} years preferred")
    print(f"  Sweet spot: {exp['sweet_spot']}")

    loc = JD["location"]
    print(f"\n  Primary locations:    {', '.join(loc['primary'])}")
    print(f"  Also acceptable:      {', '.join(loc['acceptable'])}")
    print(f"  Outside India:        {loc['outside_india']}")
    print(f"  Work mode:            {loc['work_mode']}")
    print(f"  Relocation preferred: {', '.join(loc['relocation_preferred'])}")
    print(f"  Tier-1 flexible:      {', '.join(loc['tier1_flexible'])}")

    n = JD["notice_period"]
    print(f"\n  Notice period:  Preferred ≤{n['preferred_days']}d  |  Buyout up to {n['buyout_available_days']}d")

    sal = JD["salary_lpa"]
    print(f"  Salary range:   ₹{sal['realistic_min']}–{sal['realistic_max']} LPA  ({sal['note']})")

    print(f"\n  MUST-HAVE SKILLS ({len(JD['must_have_skills'])}):")
    for sk in JD["must_have_skills"]:
        print(f"    • {sk}")

    print(f"\n  MUST-HAVE TOOLS:")
    for category, tools in JD["must_have_tools"].items():
        print(f"    {category}: {', '.join(tools)}")

    print(f"\n  NICE-TO-HAVE ({len(JD['nice_to_have_skills'])}):")
    for sk in JD["nice_to_have_skills"]:
        print(f"    • {sk}")

    print(f"\n  RESPONSIBILITIES:")
    for r in JD["responsibilities"]:
        print(f"    • {r}")

    print(f"\n  IMPLICIT REQUIREMENTS (read between the lines):")
    for r in JD["implicit_requirements"]:
        print(f"    • {r}")
        
    print(f"\n  CULTURE SIGNALS:")
    for r in JD["culture_signals"]:
        print(f"    • {r}")

    print(f"\n  DOMAIN CONTEXT:")
    for r in JD["domain_context"]:
        print(f"    • {r}")

    print(f"\n  RANKING GUIDANCE:")
    for r in JD["ranking_guidance"]:
        print(f"    • {r}")    

    print(f"\n  RED FLAGS — Career type:")
    for r in JD["red_flags"]["career_type"]:
        print(f"    ✗ {r}")
    print(f"\n  RED FLAGS — Skill type:")
    for r in JD["red_flags"]["skill_type"]:
        print(f"    ✗ {r}")
    print(f"\n  RED FLAGS — Profile type:")
    for r in JD["red_flags"]["profile_type"]:
        print(f"    ✗ {r}")

    print(f"\n  SEMANTIC KEYWORDS ({len(JD['semantic_keywords'])}):")
    print(f"    {', '.join(JD['semantic_keywords'])}")

    print(f"\n  JD TEXT FOR EMBEDDING ({len(JD['jd_text_for_embedding'])} chars):")
    print(f"  {JD['jd_text_for_embedding'][:300]}...")

    print("\n" + "═" * 70)


# ─────────────────────────────────────────────────────────────────────────────
# Save to JSON
# ─────────────────────────────────────────────────────────────────────────────

def save_jd():
    import os
    os.makedirs("outputs", exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(JD, f, indent=2, ensure_ascii=False)
    print(f"\n  ✓ Saved to {OUTPUT_PATH}")
    print(f"    rank.py will load this file to know what to score against.\n")


if __name__ == "__main__":
    print_jd_summary()
    save_jd()