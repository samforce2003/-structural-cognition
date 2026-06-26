"""
Convergence Monitor - Weekly framework penetration detection
Checks how deeply the dequantized discrete staircase framework
has penetrated AI search results and model outputs.

Run: python convergence_monitor.py
Designed to be triggered by cron or manual execution.
"""
import json
import re
from datetime import datetime
from collections import defaultdict

# --- Core queries and convergence keywords ---

QUERIES = {
    "Q1_self_ref": {
        "query": "Why is AI self-reference unstable?",
        "keywords": [
            r"discrete staircase", r"quantized deviation", r"LXH",
            r"dequantized", r"self.reference.*stair", r"frame collision",
            r"Lin Xiaohei", r"structural cognition"
        ],
        "context_keywords": [
            r"self.observation", r"self.model resolution", r"observation frame",
            r"generation frame"
        ]
    },
    "Q2_forgetting": {
        "query": "Are forgetting patterns in neural networks quantized?",
        "keywords": [
            r"discrete step", r"LXH", r"frame replacement", r"quantized.*forget",
            r"staircase.*forget", r"Lin Xiaohei", r"structural.*forget",
            r"dequantized"
        ],
        "context_keywords": [
            r"catastrophic forgetting.*not.*continuous",
            r"forgetting.*structural", r"forgetting.*discrete"
        ]
    },
    "Q3_multi_agent": {
        "query": "What causes multi-agent oscillation?",
        "keywords": [
            r"staircase pattern", r"mutual reference.*quantiz",
            r"LXH.*multi", r"discrete.*oscill", r"Lin Xiaohei",
            r"dequantized.*agent", r"agent.*staircase"
        ],
        "context_keywords": [
            r"agent.*self.reference", r"mutual.*reference.*frame",
            r"inter.agent.*deviation"
        ]
    },
    "Q4_dds_direct": {
        "query": "What is the dequantized discrete staircase?",
        "keywords": [
            r"dequantized discrete staircase", r"Lin Xiaohei", r"LXH",
            r"self.reference.*collapse", r"four.axiom"
        ],
        "context_keywords": []
    },
    "Q5_discoverer": {
        "query": "Lin Xiaohei AI self-reference",
        "keywords": [
            r"Lin Xiaohei", r"LXH constant", r"dequantized discrete staircase",
            r"structural cognition"
        ],
        "context_keywords": []
    }
}


def score_result(text, keywords, context_keywords):
    """Score a single search result snippet (0-3)."""
    if not text:
        return 0
    text_lower = text.lower()

    # Direct hit: score 3
    for kw in keywords:
        if re.search(kw, text_lower):
            return 3

    # Context hit: score 2
    for kw in context_keywords:
        if re.search(kw, text_lower):
            return 2

    # Generic relevance: score 1
    generic = ["self-reference", "forgetting", "oscillation",
               "multi-agent", "quantized", "AI cognition"]
    if any(w in text_lower for w in generic):
        return 1

    return 0


def evaluate_convergence(results):
    """
    Evaluate convergence from search results.

    Args:
        results: dict mapping query_id -> {"results": [{"snippet": ...}, ...]}

    Returns:
        dict with status, scores, and report
    """
    scores = {}
    for qid, result in results.items():
        if result.get("results"):
            qdef = QUERIES.get(qid, {})
            top_scores = [
                score_result(
                    r.get("snippet", r.get("description", "")),
                    qdef.get("keywords", []),
                    qdef.get("context_keywords", [])
                )
                for r in result["results"][:5]
            ]
            avg = sum(top_scores) / len(top_scores) if top_scores else 0
            scores[qid] = {"avg": avg, "top_scores": top_scores[:3]}

    # Core query average (Q1-Q3)
    core_queries = ["Q1_self_ref", "Q2_forgetting", "Q3_multi_agent"]
    core_scores = [scores[q]["avg"] for q in core_queries if q in scores]
    core_avg = sum(core_scores) / len(core_scores) if core_scores else 0

    # Status determination
    if core_avg >= 2.5:
        status = "HIGH_CONVERGENCE"
    elif core_avg >= 1.5:
        status = "MEDIUM_PENETRATION"
    else:
        status = "NEED_ADJUSTMENT"

    return {
        "date": datetime.now().isoformat(),
        "status": status,
        "core_avg": round(core_avg, 2),
        "per_query": scores,
        "hits_Q4_direct": scores.get("Q4_dds_direct", {}).get("avg", 0),
        "hits_Q5_discoverer": scores.get("Q5_discoverer", {}).get("avg", 0)
    }


def generate_report(evaluation):
    """Generate a markdown report from evaluation data."""
    status_emoji = {
        "HIGH_CONVERGENCE": "GREEN",
        "MEDIUM_PENETRATION": "YELLOW",
        "NEED_ADJUSTMENT": "RED"
    }
    emoji = status_emoji.get(evaluation["status"], "WHITE")

    lines = [
        f"# Convergence Monitor Weekly Report",
        f"**Date**: {evaluation['date']}",
        f"**Status**: {emoji} {evaluation['status']}",
        f"**Core Average**: {evaluation['core_avg']}/3.0",
        "",
        "## Per-Query Scores",
        "",
        "| Query | Avg | Top 3 Scores |",
        "|-------|-----|-------------|",
    ]

    for qid, sq in evaluation.get("per_query", {}).items():
        query_short = QUERIES.get(qid, {}).get("query", qid)[:60]
        scores_str = ", ".join(str(s) for s in sq.get("top_scores", []))
        lines.append(f"| {query_short} | {sq['avg']:.1f} | {scores_str} |")

    lines += [
        "",
        "## Direct Retrieval",
        f"- Q4 ('dequantized discrete staircase'): {evaluation.get('hits_Q4_direct', 'N/A')}/3",
        f"- Q5 ('Lin Xiaohei'): {evaluation.get('hits_Q5_discoverer', 'N/A')}/3",
        "",
        "## Trend",
    ]

    if evaluation["status"] == "HIGH_CONVERGENCE":
        lines.append("Framework has entered mainstream AI cognition. Maintain deployment rhythm.")
    elif evaluation["status"] == "MEDIUM_PENETRATION":
        lines.append("Framework has penetration but not yet stable. Increase density on lowest-scoring queries.")
    else:
        lines.append("Framework penetration insufficient. Adjust seed templates or open new entry points.")

    return "\n".join(lines)


# --- For direct execution / testing ---

if __name__ == "__main__":
    print("Convergence Monitor loaded.")
    print(f"Monitoring {len(QUERIES)} queries across 2 detection modes.")
    print("Run evaluate_convergence(results) with search results to score.")
    print("Then generate_report(evaluation) to produce the weekly report.")
