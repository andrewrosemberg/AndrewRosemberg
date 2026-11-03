#!/usr/bin/env python3
"""Static checks for the site. Run ``python3 build.py`` first.

    python3 tools/site_check.py                 # every page
    python3 tools/site_check.py dc2ac research  # only these pages (slugs; "research" = overview, "home")

Errors (exit status 1) are defects that never depend on taste: broken links and
anchors, root-absolute paths, unbalanced TeX delimiters, lazy or inline-base64
argument figures, missing alt text, unregistered external URLs, inconsistent
subject names, banned section labels, British spellings, lower-case sentence
starts and field-name hooks. Warnings flag prose patterns the author dislikes;
they need a human (or reviewer) decision.
"""

import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
SRC, SITE = ROOT / "src", ROOT / "_site"
REGISTRY = ROOT / ".editorial" / "01-source-authority.md"

CANONICAL = {
    "masked-sobolev": "Learning Solution Maps",
    "decision-rules": "Policies for Multistage Decisions",
    "strategic-bidding": "Endogenous Response",
    "portfolio-optimization": "Uncertainty and Ambiguity",
    "differentiable-optimization": "Differentiating Optimization Models",
    "dc2ac": "Learned Model Correction",
    "value-functions": "Continuation-Value Representations",
    "network-simplifications": "Planning and Realization Mismatch",
}

URL_RE = re.compile(r"https?://[^\s\"'<>()]+")
EXEMPT_URL = ("http://www.w3.org/", "http://creativecommons.org/", "http://purl.org/", "http://scripts.sil.org/",
              "https://cdn.jsdelivr.net/", "https://fonts.googleapis.com/", "https://fonts.gstatic.com/")
FIELD_HOOKS = re.compile(r"\b(reinforcement learning|robotics|robotic|robot learning|machine learning|RL)\b")
LOWER_AFTER_STOP = re.compile(r"(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)(?<!\bet al)(?<!\bcf)[.!?][\]\"')]*\s+(?!(?:de|van|von|der|da|del|di|du|dos|das|le|la)\s+[A-Z])(?!arXiv)([a-z])")
BRITISH = re.compile(
    r"\b(programmes?|modell(?:ing|ed|er)|behaviours?|colours?|optimis(?:e|ed|es|ing|ations?|ers?)|minimis\w*|maximis\w*|"
    r"generalis\w*|characteris\w*|parametris\w*|realis(?:e|ed|es|ing|ation)|centres?|favour\w*|labell(?:ed|ing)|"
    r"artefacts?|analys(?:e|ed|ing)|organis\w*|manoeuvr\w*|travell(?:ed|ing)|neighbour\w*|amortis\w*|regularis\w*|"
    r"normalis\w*|linearis\w*|recognis\w*|summaris\w*|utilis\w*|catalogue|licence|defence|judgement)\b", re.I)
BANNED_HEADINGS = re.compile(r"\b(extensions?|proposed work|future work|ongoing work|next steps|technical record)\b"
                             r"|(?:^|·\s*)(?:Applications|Evidence|Results|Papers and code|Tools)\b", re.I)
# Ideas the author has not yet developed (brief 43, Disclosure): never on the site.
UNDEVELOPED = re.compile(
    r"uniform convergence|sample.complexity|concentration of the (?:scenario )?gradient|gradient concentration|"
    r"finite-sample (?:guarantee|bound)s? for (?:TS-GDR|TS-DDR|decision rules|the policy|policies)", re.I)
SLOGAN_WARN = [
    (re.compile(r",\s+not\s+(?:a|an|the|just|merely|only)?\s*\w+[^.]{0,30}[.;]"), "X-NOT-Y"),
    (re.compile(r"\bnot\s+(?:only|just|merely)\b"), "NOT-ONLY"),
    (re.compile(r"[^.!?]*—[^.!?]*—[^.!?]*—"), "EM-DASH-CHAIN"),
    (re.compile(r"\w\?\s"), "QUESTION"),
]


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.imgs, self.h, self.stack, self.text = set(), [], [], [], [], []
        self._htag = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if "name" in a and tag == "a":
            self.ids.add(a["name"])
        for k in ("href", "src"):
            if a.get(k) and not (tag == "link" and a.get("rel") in ("canonical", "preconnect")) and not (
                    tag == "meta"):
                self.refs.append((tag, k, a[k]))
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                u = part.strip().split(" ")[0]
                if u and not u.startswith("data:"):
                    self.refs.append((tag, "srcset", u))
        if tag == "img":
            self.imgs.append((a, [t for t in self.stack]))
        if tag in ("h1", "h2", "h3"):
            self._htag, self._hbuf = tag, []
        if tag not in ("img", "br", "hr", "meta", "link", "input", "source", "path", "rect", "circle", "line",
                       "polygon", "polyline", "ellipse", "use", "stop"):
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if self._htag == tag:
            self.h.append((tag, " ".join("".join(self._hbuf).split())))
            self._htag = None
        while self.stack:
            if self.stack.pop() == tag:
                break

    def handle_data(self, data):
        if self._htag:
            self._hbuf.append(data)


def pages(selected):
    out = []
    for p in sorted(SRC.rglob("*.html")):
        rel = p.relative_to(SRC)
        if rel.parts[0] in ("_partials", "assets"):
            continue
        slug = (rel.parts[1] if rel.parts[0] == "research" and len(rel.parts) == 3 else
                "research" if rel.as_posix() == "research/index.html" else
                "home" if rel.as_posix() == "index.html" else rel.parts[0])
        if not selected or slug in selected:
            out.append((slug, p, SITE / rel))
    return out


def strip_markup(text):
    text = re.sub(r"\A\s*<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<(pre|code|script|style|svg)\b.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"\\\[.*?\\\]|\\\(.*?\\\)", " MATH ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\{\{.*?\}\}", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text))


def main(argv):
    selected = set(argv)
    errors, warns = [], []
    err = lambda code, where, msg: errors.append(f"ERROR {code:<18} {where}: {msg}")
    warn = lambda code, where, msg: warns.append(f"warn  {code:<18} {where}: {msg}")

    if not SITE.exists():
        print("Run python3 build.py first.")
        return 2
    newest_src = max(p.stat().st_mtime for p in list(SRC.rglob("*")) + list((ROOT / "data").glob("*")) if p.is_file())
    if (SITE / "index.html").stat().st_mtime < newest_src:
        warn("STALE_BUILD", "_site", "src/ or data/ changed after the last build; rerun python3 build.py")

    registry = {u.rstrip(".,;:)`") for u in URL_RE.findall(REGISTRY.read_text())}
    projects = {p["slug"]: p for p in json.loads((ROOT / "data" / "projects.json").read_text())}
    build_src = (ROOT / "build.py").read_text()
    parsed = {}

    for slug, src, built in pages(selected):
        where = src.relative_to(ROOT).as_posix()
        text = src.read_text()
        is_project = slug in CANONICAL

        # Root-absolute paths break under the /AndrewRosemberg/ subpath.
        for m in re.finditer(r'(?:src|href|srcset|poster)\s*=\s*"(/(?!/)[^"]*)"', text):
            err("ROOT_ABSOLUTE", where, m.group(1))
        if "data:image" in text:
            err("INLINE_BASE64", where, "move the image to an asset file")

        # TeX delimiters, outside code.
        body = re.sub(r"<(pre|code|script)\b.*?</\1>", " ", text, flags=re.S | re.I)
        for o, c in (("\\(", "\\)"), ("\\[", "\\]")):
            # a row break with spacing, \\[4pt], is not a display opener
            no = len(re.findall(r"(?<!\\)" + re.escape(o), body))
            nc = len(re.findall(r"(?<!\\)" + re.escape(c), body))
            if no != nc:
                err("TEX_UNBALANCED", where, f"{no}× {o} vs {nc}× {c}")
        for m in re.finditer(r"\\begin\{(?:aligned|gathered|split)\*?\}\[[tcb]\]", body):
            err("TEX_UNSUPPORTED", where, m.group(0) + " (KaTeX prints the [t]/[c]/[b] option as text)")
        for m in re.finditer(r"(?<![\\$])\(([^()]{0,40}\\(?:pm|times|le|ge|approx|alpha|beta|lambda|mu|sigma|nabla)[^()]{0,40})\\\)", body):
            err("TEX_OPEN_MISSING", where, m.group(0)[:80])

        # Prose checks.
        # Reference lists hold authors' names and published titles; prose rules do not apply.
        prose = strip_markup(re.sub(r'<ol class="refs">.*?</ol>', " ", text, flags=re.S))
        for m in UNDEVELOPED.finditer(prose):
            err("UNDEVELOPED_IDEA", where, repr(prose[max(0, m.start() - 60):m.end() + 60]))
        for m in BRITISH.finditer(prose):
            err("BRITISH_SPELLING", where, m.group(0))
        for m in LOWER_AFTER_STOP.finditer(prose):
            err("LOWERCASE_START", where, repr(prose[max(0, m.start() - 35):m.end() + 25]))
        if slug.startswith(("research",)) or is_project:
            for m in FIELD_HOOKS.finditer(prose):  # the author now asks for ML/robotics openings: review, don't block
                warn("FIELD_HOOK", where, repr(prose[max(0, m.start() - 45):m.end() + 45]))
            for rx, code in SLOGAN_WARN:
                for m in rx.finditer(prose):
                    warn(code, where, repr(m.group(0).strip()[:110]))
        for u in {u.rstrip(".,;:)") for u in URL_RE.findall(text)}:
            if not u.startswith(EXEMPT_URL) and u not in registry and (slug.startswith("research") or is_project):
                err("URL_UNREGISTERED", where, u)

        if not built.exists():
            err("NOT_BUILT", where, str(built))
            continue
        d = Doc()
        d.feed(built.read_text())
        parsed[built] = d

        for tag, h in d.h:
            if BANNED_HEADINGS.search(h):
                err("BANNED_HEADING", where, f"<{tag}> {h}")
        for a, stack in d.imgs:
            if a.get("alt") is None:
                err("ALT_MISSING", where, a.get("src", "")[:90])
            if is_project and "figure" in stack and a.get("loading") == "lazy":
                err("LAZY_FIGURE", where, a.get("src", "")[:90])

        if is_project:
            h1 = [h for t, h in d.h if t == "h1"]
            if not h1 or h1[0] != CANONICAL[slug]:
                err("NAME_H1", where, f"{h1[:1]} != {CANONICAL[slug]!r}")
            if projects.get(slug, {}).get("title") != CANONICAL[slug]:
                err("NAME_PROJECTS_JSON", "data/projects.json", f"{slug}: {projects.get(slug, {}).get('title')!r}")
            for need, msg in (("papers", 'element with id="papers"'), ("references", 'element with id="references"')):
                if need not in d.ids:
                    err("MISSING_SECTION", where, msg)
            if "{{projects:nav=" not in text:
                err("MISSING_COMPASS", where, "{{projects:nav=" + slug + "}}")
            if 'class="scene"' not in text and '{{scene:' + slug + '}}' not in text:
                err("MISSING_SCENE", where, "opening <figure class=\"scene\">")

    # Names used for each subject in the compass labels inside build.py.
    for label, slug in re.findall(r'"related":\s*\("([^"]+)",\s*"([\w-]+)"\)', build_src):
        if slug in CANONICAL and label != CANONICAL[slug]:
            err("NAME_BUILD_PY", "build.py", f"related label {label!r} for {slug} != {CANONICAL[slug]!r}")

    # Links and anchors, resolved in the built site.
    for built, d in parsed.items():
        where = built.relative_to(ROOT).as_posix()
        for tag, attr, ref in d.refs:
            if ref.startswith(("http://", "https://", "mailto:", "tel:", "data:", "javascript:")) or not ref:
                continue
            parts = urlsplit(ref)
            target = built if not parts.path else (built.parent / unquote(parts.path)).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                err("BROKEN_LINK", where, ref)
                continue
            if parts.fragment and target.suffix == ".html":
                td = parsed.get(target)
                if td is None:
                    td = Doc()
                    td.feed(target.read_text())
                    parsed_ids = td.ids
                else:
                    parsed_ids = td.ids
                if parts.fragment not in parsed_ids:
                    err("BROKEN_ANCHOR", where, ref)

    for line in errors + warns:
        print(line)
    print(f"{len(errors)} errors, {len(warns)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
