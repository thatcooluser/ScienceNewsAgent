"""Uses OpenAI gpt-4o-mini to produce a consolidated weekly digest."""

import logging
from openai import OpenAI

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, OPENAI_MODEL, TOPICS

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a science and technology editor writing a weekly digest for a curious professional.
Your reader is interested in: nuclear fusion energy, pharmaceutical advances, biotechnology,
and high-impact technical research papers being discussed by leading scientists.

Your job is to synthesize the provided articles into a clear, engaging newsletter.
Use plain language — explain jargon when needed. Be concise but don't sacrifice insight.
"""

DIGEST_PROMPT_TEMPLATE = """\
Below are {n} articles collected this week from MIT Technology Review, The Economist,
WIRED, Science, Quanta Magazine, The Guardian, arXiv, and more.

STEP 1 — FILTER: First, identify the 8 to 12 most impactful stories across all articles.
Ignore minor studies, incremental updates, or anything that does not represent a
meaningful advance. Prefer stories that are novel, significant, or widely covered.

STEP 2 — CROSS-COVERAGE: Articles that share the same story have already been grouped.
If an article has an "ALSO COVERED BY" field, include that information in your output
using the *(Also covered by: ...)* line shown in the format below.

STEP 3 — WRITE the digest, grouped into these sections (skip only if truly no articles fit):
1. Nuclear Fusion & Energy
2. Pharmaceuticals & Drug Discovery
3. Biotechnology & Gene Editing
4. Notable Research Papers
5. Quick Takes

CRITICAL FORMAT RULE — every story must follow this exact pattern:

**[Article Title](URL)** — *Source Name*
*(Also covered by: Source B, Source C)*   ← include this line only when 2+ outlets ran the same story
Write 2 to 4 sentences in plain English: what happened or was discovered, why it matters,
and what a non-scientist should take away. Spell out technical terms on first use.
Do NOT skip the explanation. Do NOT merge two different stories into one entry.

Then on a new line, add a 🌍 **Public Impact** paragraph of 2 to 4 sentences explaining
how this development could affect ordinary people's lives — their health, energy bills,
food, jobs, or daily choices. Be concrete and relatable. Avoid abstract statements like
"this could change everything." Instead say things like "patients with X condition may
see new treatments within 5 years" or "this could reduce household electricity costs."

Example of correct output:
**[Scientists Achieve Record Plasma Temperature](https://example.com)** — *Physics World*
*(Also covered by: The Economist, WIRED)*
Researchers heated plasma — the super-hot electrically charged gas inside a fusion reactor —
to 150 million degrees Celsius, three times hotter than the sun's core. This is a key
milestone on the path to fusion power because sustaining extreme temperatures is one of
the hardest engineering challenges. It is the highest temperature ever recorded in a
controlled fusion device.
🌍 **Public Impact:** If fusion power becomes viable, it could provide virtually unlimited
clean electricity with no carbon emissions and minimal radioactive waste. Household energy
bills could fall significantly, and countries would no longer depend on fossil fuel imports.
Most experts estimate commercial fusion is still 15–20 years away, but milestones like this
bring that timeline closer.

End with **Editor's Pick** — one story with 2 sentences on why it is the most important
development this week.

--- ARTICLES ---
{articles_block}
"""


def _build_articles_block(articles: list[dict]) -> str:
    lines = []
    for i, a in enumerate(articles, 1):
        also = ", ".join(a.get("also_covered_by", []))
        also_line = f"ALSO COVERED BY: {also}\n" if also else ""
        lines.append(
            f"[{i}] SOURCE: {a['source']}\n"
            f"{also_line}"
            f"TITLE: {a['title']}\n"
            f"URL: {a['url']}\n"
            f"DATE: {a['published']}\n"
            f"SUMMARY: {a['summary']}\n"
        )
    return "\n---\n".join(lines)


def summarize(articles: list[dict]) -> str:
    """
    Send articles to OpenAI and return the formatted digest as Markdown.
    Falls back to a plain listing if the API call fails.
    """
    if not articles:
        return "No relevant articles were found this week."

    client = OpenAI(api_key=OPENAI_API_KEY)
    articles_block = _build_articles_block(articles)
    user_prompt = DIGEST_PROMPT_TEMPLATE.format(
        n=len(articles),
        articles_block=articles_block,
    )

    log.info("Sending %d articles to OpenAI (%s)…", len(articles), OPENAI_MODEL)
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=3500,
        )
        digest = response.choices[0].message.content.strip()
        usage = response.usage
        log.info(
            "Tokens used — input: %d, output: %d (est. cost: $%.4f)",
            usage.prompt_tokens,
            usage.completion_tokens,
            (usage.prompt_tokens * 0.15 + usage.completion_tokens * 0.60) / 1_000_000,
        )
        return digest
    except Exception as exc:
        log.error("OpenAI call failed: %s", exc)
        return _fallback_digest(articles)


def _fallback_digest(articles: list[dict]) -> str:
    lines = ["**Weekly Tech & Science Digest** (AI summarization unavailable)\n"]
    for a in articles:
        lines.append(f"- [{a['title']}]({a['url']}) — {a['source']} ({a['published']})")
    return "\n".join(lines)
