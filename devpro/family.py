"""Model families: the member staffing each category, and the overlay text a family
fills at a definition's anchors. One `Family` instance per family, a module of
`devpro.families` each, selected by `--family NAME`; a family is a name, never
a path.

Schema. `Family.categories` names the member staffing each of the six categories
(`vocabulary.CATEGORIES`). It is required and total: a family that omits a
category, or names a key outside the six, fails at import rather than falling
back to a partial map or to another family's members. A family name is
reservable before any observed failure motivates tuning: an empty `overlays` is
legal, but the six categories are what make the instance construct at all. Two
categories staffed by one member is legal, a statement about that family's staffing
rather than a defect.

`Family.overlays[Anchor.X]` is an `Overlay`: family-wide `text`, per-member
`members` overrides, or both. A definition exposes an anchor by placing
`hole(Anchor.X)` in its body, which renders `Render.overlay(Anchor.X)` for the
definition's category. A member override must be reachable, spelled as some
category reaches it in the family's own `categories` or in the effective
category map the devpro settings file supplies; an unreachable member is refused
when the `Render` is built, rather than kept as an override that quietly never
fires.

The category map is the model source. The devpro settings file's
`[<harness>-model-map]` section supplies it whole where the file has one;
otherwise the harness's `default_category_spec` stands in for one where it
declares one, and otherwise it is `Family.categories`. It decides
which member's overrides a definition is tuned against, and the `model:` text it
renders. Every category's rendered text is checked against the harness's model
pattern before anything is written.

Tuned and Stock. A category whose member has member overrides in this family
gets member text, winning over family-wide text per anchor, and drops out of the
banner's `stock=` list. A category whose member has zero overrides anywhere in
the family gets family-wide text only and is named in `stock=`. Stock is a legal
reported state, not a warning: it is where a family sits until probe data
motivates an override. A member holding an override for one anchor and not
another is not stock; that anchor falls back to family-wide text.

One overlay per anchor, most specific wins. At most one overlay renders per
anchor: the override for the member the definition's category maps to, otherwise
the family-wide text, otherwise nothing. Family and member texts are never
concatenated. The text renders verbatim in place, with no lead-in and no
wrapper (any lead-in belongs in the text itself), and adds no family or member
name of its own, so the family's module is the provenance record.

Never touches base. A family can only fill anchors. It has no vocabulary for
replacing, suppressing or modifying a definition's base text, and an anchor the
family does not fill renders as nothing. Base text is tuned by editing the
definition or its shared text, never from here.

Provenance discipline. Anchors are authored on demand, when an observed failure
motivates one, never pre-sprinkled speculatively: strip first, observe, patch.
Every overlay carries a comment recording the observed behavior it corrects,
against which model it was observed, and when; not what the text says, but why
it exists. Without that record a later maintainer cannot tell "still
load-bearing" from "residue from a model we no longer use".
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field

from devpro.errors import InputError
from devpro.vocabulary import CATEGORIES, IDENTIFIER, Anchor, Category


@dataclass(frozen=True)
class Overlay:
    """Text filling one anchor: family-wide text, per-member overrides, or both."""

    text: str | None = None
    members: Mapping[str, str] = field(default_factory=dict)  # member name -> override text

    def __post_init__(self) -> None:
        """Refuse an overlay filling nothing, or any text with a leading/trailing newline."""
        if self.text is None and not self.members:
            raise InputError("an overlay fills nothing (no text, no members)")
        for text in (self.text, *self.members.values()):
            if text is not None and (not text or text.startswith("\n") or text.endswith("\n")):
                raise InputError("overlay text is empty or carries an edge newline")


@dataclass(frozen=True)
class Family:
    """A model family: the member staffing each category, and its overlays keyed by anchor."""

    name: str  # "claude", "qwen3", "gemma-4"; the --family value
    categories: Mapping[Category, str]  # exactly CATEGORIES, in CATEGORIES order; no whitespace in a member
    overlays: Mapping[Anchor, Overlay] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Refuse a non-IDENTIFIER name, or categories not exactly CATEGORIES with whitespace-free members."""
        if re.fullmatch(IDENTIFIER, self.name) is None:
            raise InputError(f"family '{self.name}': name is not a strict-kebab identifier")
        if tuple(self.categories) != CATEGORIES:
            raise InputError(
                f"family '{self.name}': categories must be exactly {', '.join(CATEGORIES)}, in that order"
            )
        for category, member in self.categories.items():
            if member.split() != [member]:
                raise InputError(f"family '{self.name}': {category} must be a non-empty member name with no whitespace")
