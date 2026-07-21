"""
model_router.py
----------------
Routes each user message to the most suitable model, calls it, and
falls back gracefully if a provider fails. Same three-tier idea as the
original script (reasoning / fast / default), cleaned up with logging,
timeouts, and type hints.

Providers used (same accounts/keys as before):
  - GitHub Models inference -> gpt-4o-mini (quick answers)
                             -> deepseek-r1 (step-by-step reasoning)
  - Groq                    -> llama-3.3-70b-versatile (default / best quality)
                             -> llama-3.1-8b-instant (fallback if everything else fails)

NOTE ON A NECESSARY FIX:
  The original code called Groq's "llama-3.1-70b-versatile", which Groq has
  since decommissioned. It's swapped below for "llama-3.3-70b-versatile",
  Groq's current equivalent, so the "default" route keeps working.
"""

import os
import logging
from dataclasses import dataclass
from typing import Literal
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("model_router")

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
github_client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_API_KEY"),
)
groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

# Central place to change model names later without touching call_model()
MODELS = {
    "reasoning": "deepseek-r1",              # via GitHub Models
    "quick": "gpt-4o-mini",                  # via GitHub Models
    "default": "llama-3.3-70b-versatile",    # via Groq (best quality)
    "fallback": "llama-3.1-8b-instant",      # via Groq (always-on safety net)
}

RouteType = Literal["reasoning", "quick", "default"]

REASONING_KEYWORDS = ("solve", "math", "equation", "logic", "step by step", "proof", "derive")
QUICK_KEYWORDS = ("quick", "fast", "short", "summary", "tl;dr", "brief")


@dataclass
class ModelReply:
    text: str
    model_used: str
    route: str


def select_route(user_input: str) -> RouteType:
    """Pick a route based on simple keyword matching (same idea as the
    original script, just centralised so it's easy to tune)."""
    text = user_input.lower()
    if any(word in text for word in REASONING_KEYWORDS):
        return "reasoning"
    if any(word in text for word in QUICK_KEYWORDS):
        return "quick"
    return "default"


def _call(client: OpenAI, model: str, messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        timeout=30,
    )
    return response.choices[0].message.content


def call_model(user_input: str, messages: list[dict]) -> tuple[str, str]:
    """
    Selects a route, calls the matching model, and falls back to a fast
    Groq model if anything goes wrong. Returns (reply_text, model_used_label).
    """
    route = select_route(user_input)

    try:
        if route == "reasoning":
            reply = _call(github_client, MODELS["reasoning"], messages)
            return reply, MODELS["reasoning"]

        if route == "quick":
            reply = _call(github_client, MODELS["quick"], messages)
            return reply, MODELS["quick"]

        # default route
        reply = _call(groq_client, MODELS["default"], messages)
        return reply, MODELS["default"]

    except Exception as primary_error:
        logger.warning("Primary model call failed (route=%s): %s", route, primary_error)
        try:
            reply = _call(groq_client, MODELS["fallback"], messages)
            return reply, f"{MODELS['fallback']} (fallback)"
        except Exception as fallback_error:
            logger.error("Fallback model call also failed: %s", fallback_error)
            return (
                "Sorry, all models are unavailable right now. Please check your "
                "API keys and try again in a moment.",
                "error",
            )
