"""Track B — OKF retrieval tools.

The agent uses these to *navigate* the Open Knowledge Format bundle in knowledge/:
first list what concepts exist, then read the most relevant one. No vector DB.
"""
import os
import re

import yaml

from .. import config

_RESERVED = {"index.md", "log.md"}
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _parse_frontmatter(text: str):
    """Return (frontmatter_dict, body_str). Missing/unparseable frontmatter -> ({}, text)."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    return data, text[m.end():]


def list_concepts() -> dict:
    """List the policy concepts available in the OKF bundle.

    Returns:
        {"concepts": [{"id": str, "title": str, "description": str}, ...]}
        where `id` is the concept path without the .md suffix,
        e.g. "03-other-compassionate-unpaid-leaves/3.1-bereavement-leave-global".
    """
    root = config.KNOWLEDGE_DIR
    concepts = []
    for dirpath, _dirs, files in os.walk(root):
        for name in sorted(files):
            if not name.endswith(".md") or name in _RESERVED:
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            concept_id = rel[:-3].replace(os.sep, "/")
            with open(path, encoding="utf-8") as fh:
                fm, _ = _parse_frontmatter(fh.read())
            concepts.append(
                {
                    "id": concept_id,
                    "title": fm.get("title", concept_id),
                    "description": fm.get("description", ""),
                }
            )
    concepts.sort(key=lambda c: c["id"])
    return {"concepts": concepts}


def read_concept(concept_id: str) -> dict:
    """Read one OKF concept's content and citation.

    Args:
        concept_id: e.g. "03-other-compassionate-unpaid-leaves/3.1-bereavement-leave-global" (no .md).

    Returns:
        {"content": str, "title": str, "resource": str | None}
        where `content` is the markdown body (after the frontmatter) and
        `resource` is the frontmatter `source` (or `resource`) reference if present.
    """
    root = os.path.realpath(config.KNOWLEDGE_DIR)
    if concept_id.endswith(".md"):
        concept_id = concept_id[:-3]
    target = os.path.realpath(os.path.join(root, concept_id + ".md"))

    if not target.startswith(root + os.sep):
        return {"error": f"Invalid concept_id: {concept_id!r} escapes the knowledge bundle."}
    if not os.path.isfile(target):
        return {
            "error": f"Concept not found: {concept_id!r}. Call list_concepts() for valid ids."
        }

    with open(target, encoding="utf-8") as fh:
        fm, body = _parse_frontmatter(fh.read())

    return {
        "content": body.strip(),
        "title": fm.get("title", concept_id),
        "resource": fm.get("source") or fm.get("resource"),
    }
