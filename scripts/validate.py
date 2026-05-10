#!/usr/bin/env python3
"""Validate skills: required frontmatter fields and skills.json sync."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
SKILLS_JSON = ROOT / "skills.json"
REQUIRED_FIELDS = {"name", "description", "allowed-tools"}
KNOWN_TOOLS = {"Read", "Glob", "Grep", "Write", "Edit", "Bash", "WebFetch", "WebSearch", "Agent"}

errors = []


def fail(msg):
    errors.append(msg)
    print(f"  FAIL  {msg}")


def parse_frontmatter(path):
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    block = match.group(1)
    fm = {}
    in_metadata = False
    for line in block.splitlines():
        if line.startswith("metadata:"):
            in_metadata = True
            continue
        if in_metadata and line.startswith("  ") and ":" in line:
            key, _, val = line.strip().partition(":")
            fm[f"metadata.{key.strip()}"] = val.strip().strip('"')
        elif not line.startswith(" ") and ":" in line:
            in_metadata = False
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"')
    return fm


def main():
    with open(SKILLS_JSON) as f:
        json_skills = {s["name"]: s for s in json.load(f)["skills"]}

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    dir_names = {d.name for d in skill_dirs}
    frontmatters = {}

    # --- SKILL.md checks ---
    print("=== SKILL.md checks ===")
    before = len(errors)
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        name = skill_dir.name
        if not skill_md.exists():
            fail(f"{name}: missing SKILL.md")
            continue
        fm = parse_frontmatter(skill_md)
        if fm is None:
            fail(f"{name}: malformed frontmatter (missing --- delimiters)")
            continue
        frontmatters[name] = fm
        for field in REQUIRED_FIELDS:
            if not fm.get(field):
                fail(f"{name}: missing required field '{field}'")
        if fm.get("name") != name:
            fail(f"{name}: name field '{fm.get('name')}' does not match directory name")
        unknown_tools = set(fm.get("allowed-tools", "").split()) - KNOWN_TOOLS
        if unknown_tools:
            fail(f"{name}: unknown tool(s) in allowed-tools: {sorted(unknown_tools)}")
    added = len(errors) - before
    passed = len(skill_dirs) - added
    print(f"  {'OK' if added == 0 else '  '}    {passed}/{len(skill_dirs)} skills have valid SKILL.md\n")

    # --- skills.json completeness ---
    print("=== skills.json completeness ===")
    before = len(errors)
    for name in sorted(dir_names - set(json_skills)):
        fail(f"{name}: skill directory exists but has no entry in skills.json")
    for name in sorted(set(json_skills) - dir_names):
        fail(f"{name}: skills.json entry has no matching skills/ directory")
    for name, entry in json_skills.items():
        if not (ROOT / entry.get("path", "")).exists():
            fail(f"{name}: skills.json path '{entry.get('path')}' does not exist")
    if len(errors) == before:
        print(f"  OK    all {len(dir_names)} skills present in both skills/ and skills.json")
    print()

    # --- field sync ---
    print("=== skills.json field sync ===")
    before = len(errors)
    for name, fm in frontmatters.items():
        if name not in json_skills:
            continue
        entry = json_skills[name]
        fm_tools = set(fm.get("allowed-tools", "").split())
        json_tools = set(entry.get("allowed-tools", []))
        if fm_tools != json_tools:
            fail(
                f"{name}: allowed-tools mismatch\n"
                f"         SKILL.md:   {sorted(fm_tools)}\n"
                f"         skills.json: {sorted(json_tools)}"
            )
        fm_ver = fm.get("metadata.version", "")
        json_ver = str(entry.get("version", ""))
        if fm_ver != json_ver:
            fail(f"{name}: version mismatch — SKILL.md='{fm_ver}' skills.json='{json_ver}'")
    if len(errors) == before:
        print(f"  OK    allowed-tools and version match for all {len(frontmatters)} skills")
    print()

    if errors:
        print(f"FAILED — {len(errors)} error(s) found.")
        sys.exit(1)
    else:
        print("All checks passed.")


if __name__ == "__main__":
    main()
