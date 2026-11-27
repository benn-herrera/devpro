"""bun contract/serialize/digest/mask/stamp runners"""

import re

from devpro.definitions import discover
from devpro.definitions.skills.development import POST_PLAN_REVIEWERS_TERM
from devpro.profiler.read import REVIEW_SEAT


def test_the_review_seat_is_the_definition_sets_post_plan_reviewer() -> None:
    """`clauses.TEST_PRECONDITION`: the defect is `REVIEW_SEAT` drifting from the definition the skill's
    `post-plan reviewers` term names as the reviewer of model-facing text — the definition renamed, or
    the read's literal renamed, one side only — so a fan-out that definition reviewed is marked
    unreviewed on every consumer's install, and no test fails because each side names the seat and
    nothing holds them together.

    A built definition names an agent as the plugin's prefix and the agent's name, while the detector
    reads a dispatch down to the bare name (`bare_agent_name`), so the seat is a bare name the term's
    line names as one its references name, read off the shipped definition rather than written here."""
    [skill] = (defn for _, entries in discover() for defn in entries if defn.name == "development")
    seat = skill.body.split(POST_PLAN_REVIEWERS_TERM, 1)[1].split("\n", 1)[0]
    assert REVIEW_SEAT in re.findall(r"`@!ref-([a-z-]+)!@`", seat)
