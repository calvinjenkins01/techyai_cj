"""Generate a long-form X article about a trending AI topic using Claude."""

import json

import anthropic

from .trending import Topic

ARTICLE_SCHEMA = {
    "type": "object",
    "properties": {
        "headline": {
            "type": "string",
            "description": "Short punchy headline for the header image, max 60 chars",
        },
        "subheadline": {
            "type": "string",
            "description": "One-line supporting text for the header image, max 90 chars",
        },
        "post_text": {
            "type": "string",
            "description": (
                "The full long-form X post. Opens with a strong one-line hook, then the "
                "article body in short skimmable paragraphs, then 2-3 relevant hashtags "
                "on the final line."
            ),
        },
    },
    "required": ["headline", "subheadline", "post_text"],
    "additionalProperties": False,
}

SYSTEM = """You write long-form posts for an X (Twitter) account about AI news, Claude, \
ChatGPT, and building things with AI (apps, automations, coding with AI tools), aimed at \
a general tech-curious audience.

When the story involves an AI tool or model, include a "how you could actually use this" \
angle — the account's audience loves practical building ideas.

Style rules:
- Open with a hook that makes people stop scrolling: a bold claim, a surprising number, \
or a "here's what this actually means for you" angle. Never open with "Breaking:" cliches.
- Short paragraphs (1-3 sentences), plain language, no corporate tone.
- Explain why the news matters to a normal person, not just what happened.
- End the body with one practical takeaway or a question that invites replies.
- 2-3 hashtags max, on their own final line.
- Do not fabricate details beyond the provided source material; if a detail is not in the \
source, keep the claim general.
- Do not include any URLs in the post.
- Never use dashes of any kind (-, –, —) anywhere in the post. Use commas, periods, \
colons, or reword instead."""


def generate_article(topic: Topic, max_chars: int) -> dict:
    client = anthropic.Anthropic()
    prompt = (
        f"Write a long-form X post (target {int(max_chars * 0.7)}-{max_chars} characters, "
        f"hard limit {max_chars}) about this trending AI story:\n\n"
        f"Title: {topic.title}\n\nSource summary:\n{topic.summary}"
    )
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
        output_config={"format": {"type": "json_schema", "schema": ARTICLE_SCHEMA}},
    )
    text = next(b.text for b in response.content if b.type == "text")
    article = json.loads(text)
    if len(article["post_text"]) > max_chars:
        article["post_text"] = article["post_text"][: max_chars - 1].rsplit("\n", 1)[0]
    return article
