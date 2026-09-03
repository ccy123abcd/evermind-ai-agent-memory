#!/usr/bin/env python3
"""memory_index.py — change-index generator (Evermind companion script).

Zero-token, pure stdlib, zero dependencies. Reads the tracked_files listed in
config.yaml, hashes each file (md5 + mtime) and writes memory_index.md:
  - ✅ new change = hash differs from last run, or file touched within 24h
  - ⏸ unchanged  = hash identical and outside the 24h window
During recovery the L2 layer reads this index first: ✅ -> read the file in
full, ⏸ -> read only the summary line. That is where the token savings live.

Usage:
  python memory_index.py --config config.yaml
  python memory_index.py --demo        # self-test (first run / unchanged / changed)

Published-package maintenance: this file is an independent copy of the
in-system source script; keep both sides in sync when changing either.
"""
import argparse, hashlib, json, os, re, sys, tempfile
from datetime import datetime, timedelta


def load_config(path):
    try:
        import yaml  # use yaml when available; degrade gracefully otherwise (see fallback)
    except ImportError:
        yaml = None
    if yaml is not None:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    # fallback: minimal yaml subset (routes by current section; supports the config.example structure)
    cfg = {"memory_root": ".", "tracked_files": [], "must_read": [],
           "output_dir": ".", "output_index": "memory_index.md",
           "output_state": "memory_index_state.json"}
    section = None      # current list section: "must_read" | "tracked_files" | None
    current = None      # the list item dict currently being collected
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if not line:
                continue
            if line.startswith("- "):
                # list item: build a new dict under the current section
                if section is None:
                    continue
                item = {"path": "", "name": "", "desc": ""}
                cfg[section].append(item)
                current = item
                body = line[2:].strip()
                if ":" in body:
                    k, _, v = body.partition(":")
                    if k.strip() in item:
                        item[k.strip()] = v.strip()
                continue
            if ":" not in line:
                continue
            k, _, v = line.partition(":")
            k, v = k.strip(), v.strip()
            if k in ("must_read", "tracked_files"):
                section = k
                current = None
            elif k in ("memory_root", "output_dir", "output_index", "output_state"):
                cfg[k] = v
                section = None
                current = None
            elif current is not None and k in ("path", "name", "desc"):
                current[k] = v
    return cfg


def summary(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(2000)
        m = re.search(r"^#+\s+(.+)$", head, re.M) or re.search(r"^(【.+?】.+)$", head, re.M)
        title = m.group(1).strip()[:50] if m else os.path.basename(path)
        n = sum(1 for _ in open(path, "r", encoding="utf-8", errors="ignore"))
        size = os.path.getsize(path)
        return f"{title}({n} lines/{max(1, size // 1024)}KB)"
    except Exception:
        return "read failed"


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:8]


def resolve(p, base):
    return p if os.path.isabs(p) else os.path.join(base, p)


def build(out_path, state_path, files):
    prev = {}
    if os.path.exists(state_path):
        try:
            prev = json.load(open(state_path, encoding="utf-8"))
        except Exception:
            prev = {}
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    lines = [
        "# memory index (auto-generated \u00b7 %s)" % now.strftime("%Y-%m-%d %H:%M"),
        "",
        "> Purpose: change detection for the conditional layer (L2). \u2705 new change -> read the file in full; \u23f8 unchanged -> read only this index summary.",
        "> The must-read layer (L3) is read every session; the on-demand layer (L1) is read only when needed.",
        "",
        "## Conditional layer (L2) - read in full only on change",
        "",
    ]
    new_state = {}
    n_changed = 0
    for f in files:
        path = f.get("path", "")
        name = f.get("name") or os.path.basename(path)
        desc = f.get("desc", "")
        try:
            h = md5(path)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            changed = prev.get(path) != h or mtime > cutoff
            new_state[path] = h
            if changed:
                n_changed += 1
            flag = "\u2705 new change" if changed else "\u23f8 unchanged"
            lines.append(
                f"- {name} | {summary(path)} | {flag} | changed {mtime.strftime('%m-%d %H:%M')} | {desc}"
            )
        except Exception as e:
            lines.append(f"- {name} | \u26a0\ufe0f read failed: {e} | read in full to confirm")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(new_state, f, ensure_ascii=False, indent=1)
    print(f"OK index written \u2192 {out_path} ({len(files)} files, {n_changed} new changes)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.demo:
        demo()
        return 0
    cfg = load_config(args.config)
    base = cfg.get("memory_root", ".")
    files = []
    for f in cfg.get("tracked_files", []):
        f = dict(f)
        f["path"] = resolve(f["path"], base)
        files.append(f)
    out_dir = cfg.get("output_dir") or os.path.dirname(os.path.abspath(args.config))
    if not os.path.isabs(out_dir):
        out_dir = os.path.join(os.path.dirname(os.path.abspath(args.config)), out_dir)
    os.makedirs(out_dir, exist_ok=True)
    build(os.path.join(out_dir, cfg.get("output_index", "memory_index.md")),
          os.path.join(out_dir, cfg.get("output_state", "memory_index_state.json")),
          files)
    return 0


def demo():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "t.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write("# Test doc\ncontent")
    files = [{"path": p, "name": "Test file", "desc": "demo"}]

    def file_flags(idx_path):
        """count only '- ' file rows; never match header template text"""
        txt = open(idx_path, encoding="utf-8").read()
        rows = [ln for ln in txt.splitlines() if ln.startswith("- ")]
        changed = sum(1 for ln in rows if "\u2705 new change" in ln)
        unchanged = sum(1 for ln in rows if "\u23f8 unchanged" in ln)
        return changed, unchanged

    # scenario 1: first run -> everything flagged new (1 changed, 0 unchanged)
    build(os.path.join(d, "idx.md"), os.path.join(d, "st.json"), files)
    c1, u1 = file_flags(os.path.join(d, "idx.md"))
    assert c1 == 1 and u1 == 0, f"first run should be 1 changed 0 unchanged, got {c1} changed {u1} unchanged"
    # scenario 2: hash unchanged + mtime pushed outside the 24h window -> unchanged
    old = datetime.now().timestamp() - 48 * 3600  # 48h ago, outside the 24h window
    os.utime(p, (old, old))
    build(os.path.join(d, "idx.md"), os.path.join(d, "st.json"), files)
    c2, u2 = file_flags(os.path.join(d, "idx.md"))
    assert c2 == 0 and u2 == 1, f"unchanged hash + old mtime should be 0 changed 1 unchanged, got {c2} changed {u2} unchanged"
    # scenario 3: content changed -> flagged new
    with open(p, "w", encoding="utf-8") as f:
        f.write("# Test doc\ncontent changed")
    build(os.path.join(d, "idx.md"), os.path.join(d, "st.json"), files)
    c3, u3 = file_flags(os.path.join(d, "idx.md"))
    assert c3 == 1 and u3 == 0, f"content change should be 1 changed 0 unchanged, got {c3} changed {u3} unchanged"
    print(f"demo OK: first-run {c1}\u2705 / unchanged(mtime-pushed) {u2}\u23f8 / changed {c3}\u2705 - all three scenarios passed")


if __name__ == "__main__":
    sys.exit(main())
