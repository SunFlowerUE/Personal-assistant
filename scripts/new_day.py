#!/usr/bin/env python3
"""生成当天的空白数据模板。已存在则跳过，不会覆盖已填数据。"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

TEMPLATES = {
    "diet": """---
date: {date}
type: diet
confidence: estimated
meals:
  - time: ""
    name: ""
    items: []
    kcal: null
    protein_g: null
totals:
  kcal: null
  protein_g: null
photos: []
---

# {date} 饮食

<!-- 照片放 media/diet/ 后在此引用，例如 ![](../../media/diet/{date}-breakfast.jpg) -->
<!-- confidence: measured=实测/包装标识 estimated=照片推算 corrected=人工修正 -->
""",
    "training": """---
date: {date}
type: training
session: ""
duration_min: null
rpe: null
exercises:
  - name: ""
    sets: []
    volume_kg: null
volume_kg: null
videos: []
---

# {date} 训练

<!-- 训练容量 = sum(次数 x 重量)。视频存 media/training/ 后在此引用 -->
""",
    "sleep": """---
date: {date}
type: sleep
bedtime: ""
wake: ""
duration_h: null
deep_min: null
rem_min: null
hrv: null
resting_hr: null
source: ""
---

# {date} 睡眠

<!-- source 填设备名（如 华为手环/Apple Watch/手填）。没有设备就手填 duration_h -->
""",
    "work": """---
date: {date}
type: work
focus_h: null
projects: []
interruptions: null
deep_work_blocks: null
---

# {date} 工作
""",
    "family": """---
date: {date}
type: family
mood: null
---

# {date} 家庭生活

<!-- 自由文本。这部分不追求结构化，记下来本身就有价值 -->
""",
    "body": """---
date: {date}
type: body
weight_kg: null
body_fat_pct: null
note: ""
---

# {date} 身体数据

<!-- 固定晨起空腹、如厕后测，每周至少 1 次 -->
<!-- 这是校准整条饮食/训练闭环的基准信号，比照片算热量可信得多 -->
""",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None, help="YYYY-MM-DD，默认今天")
    ap.add_argument("--only", default=None, help="只生成某一类，如 diet")
    args = ap.parse_args()

    date = args.date or dt.date.today().isoformat()
    made = []
    for cat, tpl in TEMPLATES.items():
        if args.only and cat != args.only:
            continue
        d = DATA / cat
        d.mkdir(parents=True, exist_ok=True)
        f = d / f"{date}.md"
        if f.exists():
            continue
        f.write_text(tpl.format(date=date), encoding="utf-8")
        made.append(str(f.relative_to(ROOT)))

    if made:
        print(f"已生成 {len(made)} 个文件：")
        for m in made:
            print("  " + m)
    else:
        print("未生成任何文件（已存在，或 --only 指定了不存在的分类）。")
        print("可用分类: " + ", ".join(TEMPLATES))


if __name__ == "__main__":
    main()