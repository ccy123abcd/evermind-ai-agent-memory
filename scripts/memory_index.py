#!/usr/bin/env python3
"""memory_index.py — 变更检测索引生成(TXJ Tiered Memory 配套脚本,通用版)

0 token、纯标准库、零依赖。读 config.yaml 中列出的 tracked_files,
为每个文件算 md5 + mtime,生成 memory_index.md:
  - ✅新变更 = 哈希与上次不同,或 24h 内改过(防跨天漏标)
  - ⏸未变更 = 哈希没变且不在 24h 窗口
恢复记忆时:L2 层先看本索引,标 ✅ 才读全文,⏸ 只读摘要行——省 token 的关键。

用法:
  python memory_index.py --config config.yaml
  python memory_index.py --demo        # 三场景自测(首次✅/未变⏸/变更✅)

发布版维护:本文件是发布包独立副本,与体系内源脚本各自演进;
改动请同步两侧,防两头漂移。
"""
import argparse, hashlib, json, os, re, sys, tempfile
from datetime import datetime, timedelta


def load_config(path):
    try:
        import yaml  # 有 yaml 用 yaml;没有则退化(见 fallback)
    except ImportError:
        yaml = None
    if yaml is not None:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    # fallback:极简 yaml 子集(按当前节分流,支持 config.example 结构)
    cfg = {"memory_root": ".", "tracked_files": [], "must_read": [],
           "output_dir": ".", "output_index": "memory_index.md",
           "output_state": "memory_index_state.json"}
    section = None      # 当前列表节: "must_read" | "tracked_files" | None
    current = None      # 当前正在收集的列表项 dict
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if not line:
                continue
            if line.startswith("- "):
                # 列表项:构造新 dict 挂到当前节
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
        return f"{title}({n}行/{max(1, size // 1024)}KB)"
    except Exception:
        return "读失败"


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
        "# 记忆索引(自动生成 · %s)" % now.strftime("%Y-%m-%d %H:%M"),
        "",
        "> 用途:条件读层(L2)变更检测。✅新变更→读全文;⏸未变更→只读本索引摘要。",
        "> 必读层(L3)每次直读;按需层(L1)用到才查。",
        "",
        "## 条件读层(L2)— 变更才读全文",
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
            flag = "✅新变更" if changed else "⏸未变更"
            lines.append(
                f"- {name} | {summary(path)} | {flag} | 改于 {mtime.strftime('%m-%d %H:%M')} | {desc}"
            )
        except Exception as e:
            lines.append(f"- {name} | ⚠️读取失败: {e} | 建议读全文确认")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(new_state, f, ensure_ascii=False, indent=1)
    print(f"OK 索引已生成 → {out_path}({len(files)} 文件,新变更 {n_changed} 个)")


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
        f.write("# 测试文档\n内容")
    files = [{"path": p, "name": "测试", "desc": "demo"}]

    def file_flags(idx_path):
        """只统计 '- ' 开头文件行的 flag,不匹配表头模板文字"""
        txt = open(idx_path, encoding="utf-8").read()
        rows = [ln for ln in txt.splitlines() if ln.startswith("- ")]
        changed = sum(1 for ln in rows if "✅新变更" in ln)
        unchanged = sum(1 for ln in rows if "⏸未变更" in ln)
        return changed, unchanged

    # 场景1:首次生成 → 应标新变更(全 ✅,无 ⏸)
    build(os.path.join(d, "idx.md"), os.path.join(d, "st.json"), files)
    c1, u1 = file_flags(os.path.join(d, "idx.md"))
    assert c1 == 1 and u1 == 0, f"首次生成应 1✅0⏸,实测 {c1}✅{u1}⏸"
    # 场景2:哈希未变 + mtime 拨出 24h 窗口 → 应标未变更
    old = datetime.now().timestamp() - 48 * 3600  # 48h 前,超出 24h 窗口
    os.utime(p, (old, old))
    build(os.path.join(d, "idx.md"), os.path.join(d, "st.json"), files)
    c2, u2 = file_flags(os.path.join(d, "idx.md"))
    assert c2 == 0 and u2 == 1, f"哈希未变+mtime旧应 0✅1⏸,实测 {c2}✅{u2}⏸"
    # 场景3:内容变更 → 应标新变更
    with open(p, "w", encoding="utf-8") as f:
        f.write("# 测试文档\n内容改了")
    build(os.path.join(d, "idx.md"), os.path.join(d, "st.json"), files)
    c3, u3 = file_flags(os.path.join(d, "idx.md"))
    assert c3 == 1 and u3 == 0, f"内容变更应 1✅0⏸,实测 {c3}✅{u3}⏸"
    print(f"demo OK:首次{c1}✅/未变(拨mtime){u2}⏸/变更{c3}✅ 三场景全过")


if __name__ == "__main__":
    sys.exit(main())
