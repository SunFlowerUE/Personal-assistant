#!/usr/bin/env python3
"""确定性聚合：从 data/ 下的 Markdown frontmatter 计算趋势表。

原则：算术归脚本，判断归模型。模型不应逐文件累加，也不应心算均值。
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import re
import sys
from pathlib import Path

import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)

METRICS = [
    ("weight_kg", "体重 kg"),
    ("kcal", "热量 kcal"),
    ("protein_g", "蛋白 g"),
    ("carbs_g", "碳水 g"),
    ("volume_kg", "训练容量 kg"),
    ("train_min", "训练时长 min"),
    ("sleep_h", "睡眠 h"),
    ("deep_min", "深睡 min"),
    ("hrv", "HRV"),
    ("focus_h", "专注 h"),
    ("interruptions", "打断次数"),
]


def read_fm(cat: str, date_str: str):
    p = DATA / cat / f"{date_str}.md"
    if not p.exists():
        return None
    m = FM.match(p.read_text(encoding="utf-8"))
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def num(v):
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


def extract(date_str: str) -> dict:
    out = {k: None for k, _ in METRICS}

    d = read_fm("diet", date_str)
    if d:
        tot = d.get("totals") or {}
        kcal = num(tot.get("kcal"))
        pro = num(tot.get("protein_g"))
        meals = d.get("meals") or []
        if kcal is None and isinstance(meals, list):
            vals = [num(m.get("kcal")) for m in meals if isinstance(m, dict)]
            vals = [v for v in vals if v is not None]
            kcal = sum(vals) if vals else None
        if pro is None and isinstance(meals, list):
            vals = [num(m.get("protein_g")) for m in meals if isinstance(m, dict)]
            vals = [v for v in vals if v is not None]
            pro = sum(vals) if vals else None
        out["kcal"], out["protein_g"] = kcal, pro
        carb = num(tot.get("carbs_g"))
        if carb is None and isinstance(meals, list):
            vals = [num(m.get("carbs_g")) for m in meals if isinstance(m, dict)]
            vals = [v for v in vals if v is not None]
            carb = sum(vals) if vals else None
        out["carbs_g"] = carb

    t = read_fm("training", date_str)
    if t:
        vol = num(t.get("volume_kg"))
        if vol is None:
            vol = 0.0
            found = False
            for ex in t.get("exercises") or []:
                if not isinstance(ex, dict):
                    continue
                ev = num(ex.get("volume_kg"))
                if ev is not None:
                    vol += ev
                    found = True
                    continue
                for s in ex.get("sets") or []:
                    if isinstance(s, dict):
                        r, w = num(s.get("reps")), num(s.get("kg"))
                        if r is not None and w is not None:
                            vol += r * w
                            found = True
            vol = vol if found else None
        out["volume_kg"] = vol
        out["train_min"] = num(t.get("duration_min"))

    s = read_fm("sleep", date_str)
    if s:
        out["sleep_h"] = num(s.get("duration_h"))
        out["deep_min"] = num(s.get("deep_min"))
        out["hrv"] = num(s.get("hrv"))

    b = read_fm("body", date_str)
    if b:
        out["weight_kg"] = num(b.get("weight_kg"))

    w = read_fm("work", date_str)
    if w:
        out["focus_h"] = num(w.get("focus_h"))
        out["interruptions"] = num(w.get("interruptions"))

    return out


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    n = len(vals)
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / (n - 1) if n > 1 else 0.0
    return {"n": n, "mean": mean, "sd": math.sqrt(var), "min": min(vals), "max": max(vals)}


def pearson(xs, ys):
    n = len(xs)
    if n < 5:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num_ = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    dy = math.sqrt(sum((b - my) ** 2 for b in ys))
    if dx == 0 or dy == 0:
        return None
    return num_ / (dx * dy)


def fmt(v, nd=1):
    return "-" if v is None else f"{v:.{nd}f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--end", default=None, help="结束日期 YYYY-MM-DD，默认今天")
    ap.add_argument("--out", default=None, help="写入文件而非 stdout")
    args = ap.parse_args()

    end = dt.date.fromisoformat(args.end) if args.end else dt.date.today()
    dates = [(end - dt.timedelta(days=i)).isoformat() for i in range(args.days - 1, -1, -1)]

    rows = [(d, extract(d)) for d in dates]
    lines = []
    lines.append(f"# 数据聚合 {dates[0]} ~ {dates[-1]}（共 {len(dates)} 天）")
    lines.append("")
    lines.append("> 由 scripts/rollup.py 生成，数值均为确定性计算。缺失一律显示 `-`，不做填充。")
    lines.append("")

    # 逐日表
    head = ["日期"] + [lbl for _, lbl in METRICS]
    lines.append("| " + " | ".join(head) + " |")
    lines.append("|" + "|".join(["---"] * len(head)) + "|")
    for d, r in rows:
        cells = [d] + [fmt(r[k], 0 if k == "interruptions" else 1) for k, _ in METRICS]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")

    # 完整度
    lines.append("## 数据完整度")
    lines.append("")
    lines.append("| 日期 | diet | training | sleep | work | family | body |")
    lines.append("|---|---|---|---|---|---|---|")
    for d in dates:
        marks = []
        for cat in ("diet", "training", "sleep", "work", "family", "body"):
            fm = read_fm(cat, d)
            marks.append("缺失" if fm is None else ("空" if not fm else "有"))
        lines.append(f"| {d} | " + " | ".join(marks) + " |")
    lines.append("")

    # 汇总
    lines.append("## 汇总统计")
    lines.append("")
    lines.append("| 指标 | n | 均值 | 标准差 | 最小 | 最大 |")
    lines.append("|---|---|---|---|---|---|")
    for k, lbl in METRICS:
        st = stats([r[k] for _, r in rows])
        if st is None:
            lines.append(f"| {lbl} | 0 | - | - | - | - |")
        else:
            lines.append(
                f"| {lbl} | {st['n']} | {st['mean']:.1f} | {st['sd']:.1f} | "
                f"{st['min']:.1f} | {st['max']:.1f} |"
            )
    lines.append("")

    # 趋势：前半 vs 后半
    half = len(rows) // 2
    if half >= 2:
        lines.append("## 趋势（前半段 vs 后半段）")
        lines.append("")
        lines.append("| 指标 | 前半均值 | 后半均值 | 变化 | 变化率 |")
        lines.append("|---|---|---|---|---|")
        for k, lbl in METRICS:
            a = stats([r[k] for _, r in rows[:half]])
            b = stats([r[k] for _, r in rows[half:]])
            if not a or not b:
                lines.append(f"| {lbl} | - | - | - | - |")
                continue
            delta = b["mean"] - a["mean"]
            rate = (delta / a["mean"] * 100) if a["mean"] else 0.0
            lines.append(
                f"| {lbl} | {a['mean']:.1f} | {b['mean']:.1f} | "
                f"{delta:+.1f} | {rate:+.1f}% |"
            )
        lines.append("")
        lines.append(f"> 前半 n<={half} 天，后半 n<={len(rows) - half} 天。样本极小，只能说『观察到』，不能说『证明』。")
        lines.append("")

    # 相关性
    lines.append("## 相关性（仅作线索，不等于因果）")
    lines.append("")
    lines.append("| A | B | n | r |")
    lines.append("|---|---|---|---|")
    pairs = [
        ("sleep_h", "focus_h"),
        ("sleep_h", "hrv"),
        ("sleep_h", "volume_kg"),
        ("protein_g", "volume_kg"),
        ("kcal", "sleep_h"),
        ("carbs_g", "deep_min"),
        ("interruptions", "focus_h"),
        ("weight_kg", "kcal"),
        ("weight_kg", "sleep_h"),
    ]
    any_pair = False
    for a, b in pairs:
        xs, ys = [], []
        for _, r in rows:
            if r[a] is not None and r[b] is not None:
                xs.append(r[a])
                ys.append(r[b])
        rr = pearson(xs, ys)
        la = dict(METRICS)[a]
        lb = dict(METRICS)[b]
        if rr is None:
            lines.append(f"| {la} | {lb} | {len(xs)} | 样本不足(n<5) |")
        else:
            any_pair = True
            tag = ""
            if abs(rr) >= 0.7:
                tag = " 强"
            elif abs(rr) >= 0.4:
                tag = " 中等"
            lines.append(f"| {la} | {lb} | {len(xs)} | {rr:+.2f}{tag} |")
    lines.append("")
    lines.append("> 单条时间序列无对照，混淆因素（考试周/出差/生病/换计划）无法排除。")
    lines.append("> r 只说明两列数字同向或反向变动，不构成因果证据。")
    lines.append("")

    text = "\n".join(lines)
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"已写入 {out}")
    else:
        print(text)


if __name__ == "__main__":
    main()