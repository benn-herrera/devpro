"""The claude family."""

from devpro.family import Family

FAMILY = Family(
    "claude",
    {
        "stem-architect": "opus",
        "stem-expert": "opus",
        "stem-mechanical": "sonnet",
        "comm-architect": "sonnet",
        "comm-expert": "sonnet",
        "comm-mechanical": "haiku",
    },
)
