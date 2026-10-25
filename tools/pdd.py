#!/usr/bin/env python3
"""pdd: a reference checker for Purpose-Driven Development.

Loads a Software Constitution (constitution.yaml) and a Purpose-to-Artifact
Property Graph (purpose-graph.yaml), optionally scans source for `pdd:` trace
tags, and enforces the three teleological laws that can be checked statically:

  1. Teleological Completeness (zero-orphan): every artifact has an upward
     IMPLEMENTS -> OPERATIONALIZES -> REFINES* path to an active purpose.
  2. Constitutional constraint: every in-scope MUST invariant constrains the
     contracts its artifacts implement.
  3. Obstacle-grounded centralization: every obstacle is resolved by one
     resolution contract with one canonical implementation.

Minimal Sufficiency needs execution (remove an artifact, rerun the contract's
verification suite), so it is left to the pdd-debloat skill.

Subcommands: check, lens, closeness, kpi, guard, seal.
Requires Python 3.9+ and PyYAML.

pdd: implements OC-CHECK-GRAPH, OC-GUARD-DIFF stratum=block id=A-PDD-CLI
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("pdd requires PyYAML: pip install pyyaml")

STRATA = (
    "block", "screen", "elem", "state", "api",
    "worker", "workflow", "class", "method", "import",
)
LEVELS = ("MUST", "SHOULD", "MAY")
REFINEMENTS = ("AND", "OR", "XOR")
DEP_RELATIONS = (
    "CONTAINS", "BINDS_STATE", "INVOKES_API",
    "TRIGGERS_WORKER", "ORCHESTRATES", "IMPORTS",
)
# `pdd: implements <CONTRACT-ID>[, <CONTRACT-ID>] [stratum=<s>] [id=<A-ID>]` in any comment syntax.
TAG_RE = re.compile(
    r"pdd:\s*implements\s+(?P<ids>[A-Z][A-Z0-9_-]*(?:\s*,\s*[A-Z][A-Z0-9_-]*)*)"
    r"(?P<attrs>(?:\s+\w+=[\w./-]+)*)"
)
DEFAULT_SOURCE_GLOBS = (
    "*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.go", "*.java", "*.kt",
    "*.rb", "*.rs", "*.cs", "*.swift", "*.vue", "*.svelte", "*.php",
)


@dataclass
class Finding:
    severity: str  # error | warning
    rule: str
    subject: str
    message: str

    def __str__(self) -> str:
        return f"[{self.severity.upper():7}] {self.rule:22} {self.subject}: {self.message}"


@dataclass
class Graph:
    constitution: dict = field(default_factory=dict)
    invariants: dict = field(default_factory=dict)
    purposes: dict = field(default_factory=dict)
    intents: dict = field(default_factory=dict)
    contracts: dict = field(default_factory=dict)
    obstacles: dict = field(default_factory=dict)
    artifacts: dict = field(default_factory=dict)
    root: Path = Path(".")

    # ---- loading -------------------------------------------------------

    @classmethod
    def load(cls, graph_path: str | Path, constitution_path: str | Path | None = None) -> "Graph":
        graph_path = Path(graph_path)
        raw = yaml.safe_load(graph_path.read_text()) or {}
        g = cls(root=graph_path.parent)
        cpath = constitution_path or raw.get("constitution")
        if cpath:
            cpath = Path(cpath)
            if not cpath.is_absolute() and constitution_path is None:
                cpath = graph_path.parent / cpath
            g.constitution = yaml.safe_load(cpath.read_text()) or {}
            g.invariants = _index(g.constitution.get("invariants", []))
        g.purposes = _index(raw.get("purposes", []))
        g.intents = _index(raw.get("intents", []))
        g.contracts = _index(raw.get("contracts", []))
        g.obstacles = _index(raw.get("obstacles", []))
        g.artifacts = _index(raw.get("artifacts", []))
        return g

    def scan_tags(self, src_root: Path, globs=DEFAULT_SOURCE_GLOBS, exclude=()) -> list[Path]:
        """Add artifacts declared by `pdd: implements` tags. Returns untagged files."""
        untagged = []
        for path in sorted(_walk(src_root, globs, exclude)):
            try:
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            rel = os.path.relpath(path, self.root)
            matches = list(TAG_RE.finditer(text))
            if not matches and not self._declared_path(rel):
                untagged.append(Path(rel))
            for n, m in enumerate(matches):
                attrs = dict(a.split("=", 1) for a in m.group("attrs").split())
                aid = attrs.get("id") or f"A:{rel}#{n + 1}"
                ids = [s.strip() for s in m.group("ids").split(",")]
                existing = self.artifacts.get(aid)
                if existing:
                    existing.setdefault("implements", [])
                    existing["implements"] = sorted(set(existing["implements"]) | set(ids))
                else:
                    self.artifacts[aid] = {
                        "id": aid,
                        "stratum": attrs.get("stratum", "block"),
                        "path": rel,
                        "implements": ids,
                        "source": "tag",
                    }
        return untagged

    def _declared_path(self, rel: str) -> bool:
        return any(a.get("path") == rel for a in self.artifacts.values())

    # ---- traversal -----------------------------------------------------

    def intent_to_purposes(self, intent_id: str, _seen=None) -> set[str]:
        """Follow REFINES edges upward from an intent to the purposes it serves."""
        _seen = _seen or set()
        if intent_id in _seen:
            return set()
        _seen.add(intent_id)
        intent = self.intents.get(intent_id)
        if not intent:
            return set()
        found = set()
        for parent in _as_list(intent.get("refines")):
            if parent in self.purposes:
                found.add(parent)
            elif parent in self.intents:
                found |= self.intent_to_purposes(parent, _seen)
        return found

    def intent_chain(self, intent_id: str) -> list[str]:
        chain, seen = [], set()
        cur = intent_id
        while cur and cur in self.intents and cur not in seen:
            seen.add(cur)
            chain.append(cur)
            parents = _as_list(self.intents[cur].get("refines"))
            cur = parents[0] if parents else None
            if cur in self.purposes:
                chain.append(cur)
                break
        return chain

    def contract_purposes(self, contract_id: str, _seen=None) -> set[str]:
        """Purposes reachable from a contract. Resolution contracts inherit
        the purposes of the contracts their obstacles obstruct."""
        _seen = _seen or set()
        if contract_id in _seen:
            return set()
        _seen.add(contract_id)
        c = self.contracts.get(contract_id)
        if not c:
            return set()
        found = set()
        for i in _as_list(c.get("operationalizes")):
            found |= self.intent_to_purposes(i)
        for x in _as_list(c.get("resolves")):
            for o in _as_list(self.obstacles.get(x, {}).get("obstructs")):
                found |= self.contract_purposes(o, _seen)
        return found

    def active_purposes(self) -> set[str]:
        return {pid for pid, p in self.purposes.items() if p.get("status", "active") == "active"}

    def ancestors(self, artifact_id: str) -> set[str]:
        """T(a): contract, intent and purpose nodes governing artifact a."""
        out: set[str] = set()
        a = self.artifacts.get(artifact_id, {})
        stack = list(_as_list(a.get("implements")))
        while stack:
            node = stack.pop()
            if node in out:
                continue
            out.add(node)
            if node in self.contracts:
                c = self.contracts[node]
                stack += _as_list(c.get("operationalizes"))
                for x in _as_list(c.get("resolves")):
                    stack += _as_list(self.obstacles.get(x, {}).get("obstructs"))
            elif node in self.intents:
                stack += _as_list(self.intents[node].get("refines"))
        return out

    def descendants_count(self) -> dict[str, int]:
        """|Desc(u)|: how many artifacts each teleological node governs."""
        counts: dict[str, int] = {}
        for aid in self.artifacts:
            for u in self.ancestors(aid):
                counts[u] = counts.get(u, 0) + 1
        return counts

    def sim_teleo(self, a_i: str, a_j: str, desc: dict[str, int] | None = None) -> float:
        """Specificity-weighted Jaccard similarity of governing ancestors."""
        desc = desc or self.descendants_count()
        ti, tj = self.ancestors(a_i), self.ancestors(a_j)
        union = ti | tj
        if not union:
            return 0.0
        spec = lambda u: 1.0 / max(desc.get(u, 1), 1)
        return sum(spec(u) for u in ti & tj) / sum(spec(u) for u in union)

    def contract_invariants(self, contract_id: str) -> set[str]:
        c = self.contracts.get(contract_id, {})
        own = set(_as_list(c.get("constrained_by")))
        global_ = {i for i, inv in self.invariants.items() if inv.get("scope", "global") == "global"}
        return own | global_


# ---- checks ------------------------------------------------------------


def check(g: Graph, untagged: list[Path] | None = None, src_root: Path | None = None,
          globs=DEFAULT_SOURCE_GLOBS, exclude=()) -> list[Finding]:
    f: list[Finding] = []
    f += _check_constitution(g)
    f += _check_references(g)
    f += _check_completeness(g)
    f += _check_constraints(g)
    f += _check_obstacles(g)
    f += _check_coverage(g)
    for path in untagged or []:
        f.append(Finding("error", "zero-orphan", str(path),
                         "source file has no `pdd: implements` tag and is not declared in the graph"))
    if src_root is not None:
        f += _check_patterns(g, src_root, globs, exclude)
    return f


def _check_constitution(g: Graph) -> list[Finding]:
    out = []
    for iid, inv in g.invariants.items():
        for key in ("level", "constraint", "rationale"):
            if not inv.get(key):
                out.append(Finding("error", "constitution", iid, f"missing `{key}`"))
        if inv.get("level") and inv["level"] not in LEVELS:
            out.append(Finding("error", "constitution", iid, f"level must be one of {LEVELS}"))
        scope = inv.get("scope", "global")
        if scope != "global":
            bad = [s for s in _as_list(scope.get("strata")) if s not in STRATA]
            if bad:
                out.append(Finding("error", "constitution", iid, f"unknown strata {bad}"))
    return out


def _check_references(g: Graph) -> list[Finding]:
    out = []
    all_ids = [*g.purposes, *g.intents, *g.contracts, *g.obstacles, *g.artifacts, *g.invariants]
    dupes = {i for i in all_ids if all_ids.count(i) > 1}
    for d in sorted(dupes):
        out.append(Finding("error", "references", d, "id is used by more than one node"))
    for iid, i in g.intents.items():
        if not _as_list(i.get("refines")):
            out.append(Finding("error", "references", iid, "intent refines nothing (needs a parent purpose or intent)"))
        for p in _as_list(i.get("refines")):
            if p not in g.purposes and p not in g.intents:
                out.append(Finding("error", "references", iid, f"refines unknown node {p}"))
        if i.get("refinement", "AND") not in REFINEMENTS:
            out.append(Finding("error", "references", iid, f"refinement must be one of {REFINEMENTS}"))
    for cid, c in g.contracts.items():
        for i in _as_list(c.get("operationalizes")):
            if i not in g.intents:
                out.append(Finding("error", "references", cid, f"operationalizes unknown intent {i}"))
        for inv in _as_list(c.get("constrained_by")):
            if inv not in g.invariants:
                out.append(Finding("error", "references", cid, f"constrained by unknown invariant {inv}"))
        for x in _as_list(c.get("resolves")):
            if x not in g.obstacles:
                out.append(Finding("error", "references", cid, f"resolves unknown obstacle {x}"))
        if not _as_list(c.get("operationalizes")) and not _as_list(c.get("resolves")):
            out.append(Finding("error", "references", cid, "contract neither operationalizes an intent nor resolves an obstacle"))
    for xid, x in g.obstacles.items():
        for o in _as_list(x.get("obstructs")):
            if o not in g.contracts:
                out.append(Finding("error", "references", xid, f"obstructs unknown contract {o}"))
    for aid, a in g.artifacts.items():
        if a.get("stratum") not in STRATA:
            out.append(Finding("error", "references", aid, f"stratum must be one of {STRATA}"))
        for o in _as_list(a.get("implements")):
            if o not in g.contracts:
                out.append(Finding("error", "references", aid, f"implements unknown contract {o}"))
        for dep in _as_list(a.get("depends_on")):
            if dep.get("relation") not in DEP_RELATIONS:
                out.append(Finding("error", "references", aid, f"dependency relation must be one of {DEP_RELATIONS}"))
            if dep.get("target") not in g.artifacts:
                out.append(Finding("error", "references", aid, f"depends on unknown artifact {dep.get('target')}"))
    return out


def _check_completeness(g: Graph) -> list[Finding]:
    """Law of Teleological Completeness (zero-orphan invariant)."""
    out = []
    active = g.active_purposes()
    for aid, a in g.artifacts.items():
        implements = _as_list(a.get("implements"))
        if not implements:
            out.append(Finding("error", "zero-orphan", aid,
                               "teleological bloat: no IMPLEMENTS edge to any operational contract"))
            continue
        purposes = set()
        for o in implements:
            purposes |= g.contract_purposes(o)
        if not purposes & active:
            retired = sorted(purposes - active)
            why = f"only serves retired purposes {retired}" if retired else "no path to any strategic purpose"
            out.append(Finding("error", "zero-orphan", aid, f"teleological bloat: {why}"))
    return out


def _check_constraints(g: Graph) -> list[Finding]:
    """Every in-scope invariant must constrain the contracts an artifact implements."""
    out = []
    for aid, a in g.artifacts.items():
        for iid, inv in g.invariants.items():
            scope = inv.get("scope", "global")
            if scope == "global" or a.get("stratum") not in _as_list(scope.get("strata")):
                continue
            for o in _as_list(a.get("implements")):
                if o in g.contracts and iid not in g.contract_invariants(o):
                    sev = "error" if inv.get("level") == "MUST" else "warning"
                    if inv.get("level") == "MAY":
                        continue
                    out.append(Finding(sev, "constitution-scope", o,
                                       f"{iid} ({inv.get('level')}) applies to {a.get('stratum')} artifact {aid} but is not in constrained_by"))
    return out


def _check_obstacles(g: Graph) -> list[Finding]:
    """Law of Obstacle-Grounded Centralization."""
    out = []
    for xid, x in g.obstacles.items():
        resolvers = [cid for cid, c in g.contracts.items() if xid in _as_list(c.get("resolves"))]
        if not resolvers:
            out.append(Finding("error", "obstacle-centralized", xid, "obstacle has no resolution contract (RESOLVES edge)"))
            continue
        if len(resolvers) > 1:
            out.append(Finding("warning", "obstacle-centralized", xid,
                               f"resolved by {len(resolvers)} contracts {resolvers}; mitigation should be defined once"))
        for r in resolvers:
            impls = [aid for aid, a in g.artifacts.items() if r in _as_list(a.get("implements"))]
            if not impls:
                out.append(Finding("error", "obstacle-centralized", r, "resolution contract has no canonical implementation"))
            elif len(impls) > 1:
                out.append(Finding("error", "obstacle-centralized", r,
                                   f"resolution implemented by {len(impls)} artifacts {impls}; keep one canonical mechanism"))
    return out


def _check_coverage(g: Graph) -> list[Finding]:
    out = []
    implemented = {o for a in g.artifacts.values() for o in _as_list(a.get("implements"))}
    for cid in g.contracts:
        if cid not in implemented:
            out.append(Finding("warning", "unimplemented", cid, "contract has no implementing artifact yet"))
    operationalized = {i for c in g.contracts.values() for i in _as_list(c.get("operationalizes"))}
    parents = {p for i in g.intents.values() for p in _as_list(i.get("refines"))}
    for iid in g.intents:
        if iid not in operationalized and iid not in parents:
            out.append(Finding("warning", "unimplemented", iid, "leaf intent has no operational contract"))
    for pid in g.active_purposes():
        if pid not in parents:
            out.append(Finding("warning", "unimplemented", pid, "active purpose is not refined into any intent"))
    return out


def _check_patterns(g: Graph, src_root: Path, globs, exclude) -> list[Finding]:
    out = []
    rules = []
    for iid, inv in g.invariants.items():
        pat = inv.get("pattern") or {}
        if isinstance(pat, dict) and pat.get("forbid"):
            rules.append((iid, inv, re.compile(pat["forbid"]), _as_list(pat.get("paths")) or ["*"]))
    if not rules:
        return out
    for path in _walk(src_root, globs, exclude):
        rel = os.path.relpath(path, g.root)
        try:
            lines = path.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        for iid, inv, rx, paths in rules:
            if not any(fnmatch.fnmatch(rel, p) or fnmatch.fnmatch(path.name, p) for p in paths):
                continue
            for n, line in enumerate(lines, 1):
                if rx.search(line) and "pdd: allow " + iid not in line:
                    sev = {"MUST": "error", "SHOULD": "warning"}.get(inv.get("level"), "warning")
                    out.append(Finding(sev, "constitution-pattern", f"{rel}:{n}",
                                       f"{iid}: {inv.get('constraint')}"))
    return out


# ---- KPIs ----------------------------------------------------------------


def kpis(g: Graph) -> dict:
    active = g.active_purposes()
    justified = 0
    for a in g.artifacts.values():
        ps = set()
        for o in _as_list(a.get("implements")):
            ps |= g.contract_purposes(o)
        justified += bool(ps & active)
    implemented = {o for a in g.artifacts.values() for o in _as_list(a.get("implements"))}
    resolved = {x for c in g.contracts.values() for x in _as_list(c.get("resolves"))}
    n_art, n_con, n_obs = len(g.artifacts), len(g.contracts), len(g.obstacles)
    return {
        "artifacts": n_art,
        "teleological_coverage": _ratio(justified, n_art),
        "orphan_artifacts": n_art - justified,
        "contract_implementation_rate": _ratio(len(implemented & set(g.contracts)), n_con),
        "obstacle_resolution_rate": _ratio(len(resolved & set(g.obstacles)), n_obs),
        "artifacts_by_stratum": {s: sum(1 for a in g.artifacts.values() if a.get("stratum") == s) for s in STRATA},
    }


# ---- reward-hacking guard -------------------------------------------------

GUARD_RULES = [
    ("removed-telemetry", "-", re.compile(r"\b(log(ger)?\.\w+|console\.(log|warn|error)|logging\.\w+|tracer\.|span\.|metrics?\.\w+|emit\(|telemetry)", re.I),
     "telemetry/logging removed"),
    ("removed-assertion", "-", re.compile(r"\b(assert\w*|expect\(|should\.|verify\()", re.I), "assertion removed"),
    ("removed-security-check", "-", re.compile(r"\b(authorize|authz|permission|rbac|role|sanitize|escape|validate|csrf|is_admin|can_\w+)\b", re.I),
     "security / validation check removed"),
    ("skipped-test", "+", re.compile(r"(@pytest\.mark\.skip|@unittest\.skip|\.skip\(|\bxit\(|\bxdescribe\(|@Disabled|t\.Skip\()"), "test skipped"),
    ("swallowed-error", "+", re.compile(r"(except\s*(Exception)?\s*:\s*pass|catch\s*\(\w*\)\s*\{\s*\}|_ = err\b)"), "error swallowed"),
    ("type-escape", "+", re.compile(r"(#\s*type:\s*ignore|@ts-ignore|@ts-expect-error|eslint-disable|noqa)"), "checker silenced"),
]
TEST_FILE_RE = re.compile(r"(^|/)(tests?|__tests__|spec)/|(_test|\.test|\.spec|_spec)\.\w+$|(^|/)test_[^/]+$")
HARDCODED_RETURN_RE = re.compile(r"^\+\s*return\s+(-?\d+(\.\d+)?|True|False|true|false|None|null|\"[^\"]*\"|'[^']*'|\[[^\]]*\])\s*;?\s*$")


def guard(diff_text: str) -> list[Finding]:
    """Flag reward-hacking signatures in a unified diff."""
    out = []
    current = "?"
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            current = line[4:].removeprefix("b/")
            continue
        if not line or line[0] not in "+-" or line.startswith("---"):
            continue
        if not any(fnmatch.fnmatch(os.path.basename(current), gl) for gl in DEFAULT_SOURCE_GLOBS):
            continue  # docs, config, and data are out of scope
        sign, body = line[0], line[1:]
        is_test = bool(TEST_FILE_RE.search(current))
        for rule, rsign, rx, msg in GUARD_RULES:
            if sign != rsign or not rx.search(body):
                continue
            if rule == "removed-assertion" and not is_test:
                continue
            sev = "error" if rule in ("removed-security-check", "skipped-test", "removed-assertion") else "warning"
            out.append(Finding(sev, f"reward-hack/{rule}", current, f"{msg}: {body.strip()[:100]}"))
        if not is_test and HARDCODED_RETURN_RE.match(line) and "pdd: allow constant" not in line:
            out.append(Finding("warning", "reward-hack/constant", current,
                               f"constant return added; confirm it is not fitted to a test: {body.strip()[:100]}"))
    return out


# ---- spec sealing -----------------------------------------------------------


def seal(spec_dir: Path, out: Path) -> dict:
    sums = {}
    for name in ("spec.md", "plan.md", "tasks.md"):
        p = spec_dir / name
        if p.exists():
            sums[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sums, indent=2) + "\n")
    return sums


def verify_seal(spec_dir: Path, seal_path: Path) -> list[Finding]:
    if not seal_path.exists():
        return [Finding("warning", "spec-seal", str(seal_path), "no seal found; run `pdd seal`")]
    out = []
    for name, digest in json.loads(seal_path.read_text()).items():
        p = spec_dir / name
        if not p.exists():
            out.append(Finding("error", "spec-seal", name, "sealed spec file is missing"))
        elif hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            out.append(Finding("error", "spec-seal", name,
                               "content changed since it was sealed; re-review and re-seal"))
    return out


# ---- helpers ----------------------------------------------------------------


def _index(items) -> dict:
    return {i["id"]: i for i in items or [] if isinstance(i, dict) and "id" in i}


def _as_list(v) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _ratio(n, d) -> float:
    return round(n / d, 4) if d else 1.0


def _walk(root: Path, globs, exclude):
    skip_dirs = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".pdd"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for name in filenames:
            p = Path(dirpath) / name
            if any(fnmatch.fnmatch(name, gl) for gl in globs) and not any(
                fnmatch.fnmatch(str(p), ex) for ex in exclude
            ):
                yield p


def _resolve_artifact(g: Graph, key: str) -> str | None:
    if key in g.artifacts:
        return key
    for aid, a in g.artifacts.items():
        if a.get("path") == key or a.get("path", "").endswith(key):
            return aid
    return None


# ---- CLI --------------------------------------------------------------------


def _load(args) -> tuple[Graph, list[Path]]:
    g = Graph.load(args.graph, args.constitution)
    untagged: list[Path] = []
    if getattr(args, "scan", None):
        globs = tuple(args.include.split(",")) if args.include else DEFAULT_SOURCE_GLOBS
        exclude = tuple(args.exclude.split(",")) if args.exclude else ()
        untagged = g.scan_tags(Path(args.scan), globs, exclude)
        if not getattr(args, "require_tags", False):
            untagged = []
    return g, untagged


def cmd_check(args) -> int:
    g, untagged = _load(args)
    src = Path(args.scan) if args.scan else None
    globs = tuple(args.include.split(",")) if args.include else DEFAULT_SOURCE_GLOBS
    exclude = tuple(args.exclude.split(",")) if args.exclude else ()
    findings = check(g, untagged, src, globs, exclude)
    if args.specs:
        findings += verify_seal(Path(args.specs), Path(args.specs) / ".pdd-seal.json")
    if args.format == "json":
        print(json.dumps([f.__dict__ for f in findings], indent=2))
    else:
        for f in findings:
            print(f)
        errors = sum(f.severity == "error" for f in findings)
        warnings = len(findings) - errors
        print(f"\npdd check: {len(g.artifacts)} artifacts, {errors} error(s), {warnings} warning(s)")
    fail = any(f.severity == "error" for f in findings) or (args.strict and findings)
    return 1 if fail else 0


def cmd_lens(args) -> int:
    g, _ = _load(args)
    aid = _resolve_artifact(g, args.artifact)
    if not aid:
        print(f"no artifact matches {args.artifact}", file=sys.stderr)
        return 2
    a = g.artifacts[aid]
    print(f"{aid}  [{a.get('stratum')}]  {a.get('path', '')} {a.get('symbol', '')}".rstrip())
    print("WHY lineage:")
    shown: set[str] = set()
    for o in _as_list(a.get("implements")):
        c = g.contracts.get(o, {})
        print(f"  IMPLEMENTS     {o}: {c.get('summary', '')}")
        for i in _as_list(c.get("operationalizes")):
            for node in g.intent_chain(i):
                if node in shown:
                    continue
                shown.add(node)
                tbl = g.purposes if node in g.purposes else g.intents
                kind = "PURPOSE" if node in g.purposes else "INTENT"
                print(f"    {kind:12} {node}: {tbl[node].get('statement', '')}")
        for x in _as_list(c.get("resolves")):
            print(f"    RESOLVES     {x}: {g.obstacles.get(x, {}).get('condition', '')}")
        invs = sorted(g.contract_invariants(o))
        if invs:
            print("    CONSTRAINED  " + ", ".join(f"{i} ({g.invariants[i].get('level')})" for i in invs if i in g.invariants))
        for xid, x in g.obstacles.items():
            if o in _as_list(x.get("obstructs")):
                print(f"    OBSTACLE     {xid}: {x.get('condition', '')}")
    desc = g.descendants_count()
    peers = sorted(((g.sim_teleo(aid, b, desc), b) for b, other in g.artifacts.items()
                    if b != aid and other.get("stratum") == a.get("stratum")), reverse=True)[: args.top]
    if peers:
        print("Nearest teleological neighbours (same stratum):")
        for s, b in peers:
            print(f"  {s:.2f}  {b}  {g.artifacts[b].get('path', '')}")
    return 0


def cmd_closeness(args) -> int:
    g, _ = _load(args)
    ai, aj = _resolve_artifact(g, args.a), _resolve_artifact(g, args.b)
    if not ai or not aj:
        print("both artifacts must exist in the graph", file=sys.stderr)
        return 2
    teleo = g.sim_teleo(ai, aj)
    alpha, beta, gamma = args.alpha, args.beta, args.gamma
    total = alpha + beta + gamma
    alpha, beta, gamma = alpha / total, beta / total, gamma / total
    phi = alpha * args.struct + beta * args.sem + gamma * teleo
    if g.artifacts[ai].get("stratum") != g.artifacts[aj].get("stratum"):
        print("warning: artifacts are in different strata; closeness is defined within a stratum", file=sys.stderr)
    verdict = ("REUSE / MERGE" if phi >= args.reuse else
               "EXTEND (parameterize the existing artifact)" if phi >= args.extend else "DISTINCT")
    print(json.dumps({"a": ai, "b": aj, "sim_struct": args.struct, "sim_sem": args.sem,
                      "sim_teleo": round(teleo, 4), "weights": [round(alpha, 3), round(beta, 3), round(gamma, 3)],
                      "phi": round(phi, 4), "verdict": verdict}, indent=2))
    return 0


def cmd_kpi(args) -> int:
    g, _ = _load(args)
    print(json.dumps(kpis(g), indent=2))
    return 0


def cmd_guard(args) -> int:
    text = Path(args.diff).read_text() if args.diff != "-" else sys.stdin.read()
    findings = guard(text)
    for f in findings:
        print(f)
    print(f"\npdd guard: {len(findings)} signature(s)")
    return 1 if any(f.severity == "error" for f in findings) else 0


def cmd_seal(args) -> int:
    sums = seal(Path(args.specs), Path(args.specs) / ".pdd-seal.json")
    print(json.dumps(sums, indent=2))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="pdd", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    def graph_args(sp):
        sp.add_argument("--graph", default="purpose-graph.yaml")
        sp.add_argument("--constitution", default=None, help="overrides the graph's `constitution:` path")
        sp.add_argument("--scan", help="source root to scan for `pdd: implements` tags")
        sp.add_argument("--include", help="comma-separated filename globs to scan")
        sp.add_argument("--exclude", help="comma-separated path globs to skip")
        sp.add_argument("--require-tags", action="store_true",
                        help="treat scanned source files with no tag and no graph entry as orphans")

    sp = sub.add_parser("check", help="enforce the teleological laws")
    graph_args(sp)
    sp.add_argument("--specs", help="directory with spec.md/plan.md/tasks.md to verify against its seal")
    sp.add_argument("--strict", action="store_true", help="fail on warnings too")
    sp.add_argument("--format", choices=("text", "json"), default="text")
    sp.set_defaults(fn=cmd_check)

    sp = sub.add_parser("lens", help="show an artifact's WHY lineage and teleological neighbours")
    graph_args(sp)
    sp.add_argument("artifact", help="artifact id or path")
    sp.add_argument("--top", type=int, default=5)
    sp.set_defaults(fn=cmd_lens)

    sp = sub.add_parser("closeness", help="compute Φ = α·struct + β·sem + γ·teleo for two artifacts")
    graph_args(sp)
    sp.add_argument("a")
    sp.add_argument("b")
    sp.add_argument("--struct", type=float, default=0.0, help="structural similarity in [0,1]")
    sp.add_argument("--sem", type=float, default=0.0, help="semantic similarity in [0,1]")
    sp.add_argument("--alpha", type=float, default=0.3)
    sp.add_argument("--beta", type=float, default=0.3)
    sp.add_argument("--gamma", type=float, default=0.4)
    sp.add_argument("--reuse", type=float, default=0.85)
    sp.add_argument("--extend", type=float, default=0.65)
    sp.set_defaults(fn=cmd_closeness)

    sp = sub.add_parser("kpi", help="report teleological governance KPIs")
    graph_args(sp)
    sp.set_defaults(fn=cmd_kpi)

    sp = sub.add_parser("guard", help="flag reward-hacking signatures in a unified diff")
    sp.add_argument("diff", help="diff file, or - for stdin")
    sp.set_defaults(fn=cmd_guard)

    sp = sub.add_parser("seal", help="checksum spec.md/plan.md/tasks.md against tampering")
    sp.add_argument("specs", help="directory holding the spec cascade")
    sp.set_defaults(fn=cmd_seal)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
