# Contributing

This repository practices what it describes.

1. Every change implements a contract in `purpose-graph.yaml`. New capability?
   Add the intent and contract first.
2. New skills go in `skills/<name>/SKILL.md` with `name` matching the folder and
   a `description` that says when to use it. Add the skill to the README table
   and to the routing table in `skills/using-pdd/SKILL.md`.
3. Changes to `tools/pdd.py` or `harnesses/` need tests in `tests/`.
4. Run before opening a PR:
   ```bash
   python -m unittest discover -s tests
   python tools/pdd.py check --scan tools --require-tags --strict
   python tools/pdd.py check --graph examples/checkout/purpose-graph.yaml --scan examples/checkout/src --require-tags --strict --specs examples/checkout/specs
   ```
5. If you edit `examples/checkout/specs/*.md`, re-seal: `python tools/pdd.py seal examples/checkout/specs`.
