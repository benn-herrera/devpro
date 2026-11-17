"""The qwen3 family."""

from devpro.family import Family

FAMILY = Family(
    "qwen3",
    {
        "stem-architect": "Qwen3.8-Flash-Next",
        "stem-expert": "Qwen3.8-Flash-Next",
        "stem-mechanical": "Qwen3.8-27B",
        "comm-architect": "Qwen3.8-Flash-Next",
        "comm-expert": "Qwen3.8-Flash-Next",
        "comm-mechanical": "Qwen3.8-27B",
    },
)
