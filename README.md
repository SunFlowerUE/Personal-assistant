# life-ledger · 本地生活数据账本

把饮食、训练、睡眠、体重、工作、家庭记成**本地 Markdown**，让 AI 出日报、看趋势、提建议，
并追踪每一条建议到底有没有用。

数据全在你自己的磁盘上，换模型、换工具、换平台都不受影响。

---

## 能做什么

### 1. 随手记，一天一文件

六种数据各一个 Markdown 文件，YAML frontmatter 存数值，正文写人话备注：

| 分类 | 记什么 |
|---|---|
| `data/diet/` | 每餐食物、热量、蛋白、碳水、脂肪、照片路径、置信度 |
| `data/training/` | 动作、重量、组数次数、训练容量、RPE、视频路径 |
| `data/sleep/` | 上床/醒来、实际睡眠、深睡、REM、HRV、睡眠效率 |
| `data/body/` | 体重、体脂率（校准整条链的基准信号） |
| `data/work/` | 专注时长、项目、打断次数 |
| `data/family/` | 自由文本 |

每个数值都带置信度标记：`measured`（实测）/ `estimated`（推算）/ `corrected`（人工修正）。

### 2. 一条命令算出趋势

`scripts/rollup.py` 做所有算术——AI 不心算，数字才可信：

    python scripts/rollup.py --days 30

输出五块内容：

```
# 数据聚合 2026-01-01 ~ 2026-01-30（共 30 天）

| 日期 | 体重 kg | 热量 kcal | 蛋白 g | 碳水 g | 训练容量 kg | 睡眠 h | 深睡 min | HRV | 专注 h |
|---|---|---|---|---|---|---|---|---|---|
| 2026-01-01 | 70.2  | 2100 | 145 | 180 | 3556 | 7.4 | 85 | 62 | 5.5 |
| 2026-01-02 | 70.0  | 1980 | 138 | 165 | -    | 6.8 | 72 | 58 | 4.0 |
...

## 数据完整度        ← 哪天缺了哪类数据，一眼看到
## 汇总统计          ← 均值 / 标准差 / 最小 / 最大
## 趋势（前半 vs 后半）← 变化 + 变化率
## 相关性            ← 睡眠 vs 专注、体重 vs 热量……附样本量，并标注「不等于因果」
```

缺失一律显示 `-`，**不做任何填充或插值**。

### 3. 日报与周报

- **日报**：当天数据摘要 + **一条**最该改的事（不列十条）
- **周报**：趋势 + 最多 3 条建议，每条都写清「什么变化算有效」

### 4. 追踪建议到底有没有用

`reviews/advice-ledger.md` 是核心。每条建议记：

| 提出日期 | 建议 | 依据指标 | 采纳 | 观察窗口 | 判定标准 | 实测变化 | 结论 |
|---|---|---|---|---|---|---|---|

**判定标准在提建议时就写死**，不允许事后编。到期回填实测结果，给出保留 / 调整 / 废弃。
每 4 周统计采纳率与有效率——采纳率低说明建议不切实际，有效率低说明依据指标选错了。

### 5. 微信随手录入（可选）

不想开电脑时，用手机发一条带标签的消息即可：

    [睡眠] + 截图
    [饮食] 午餐 + 照片
    [训练] 卧推 60kg 8x3
    [体重] 70.2
    [日报]   [周报]   [趋势] 近30天   [修正]   [回填]

---

## 功能清单

| 功能 | 说明 |
|---|---|
| `scripts/new_day.py` | 生成当天六类空白模板，已存在则跳过（不会覆盖已填数据） |
| `scripts/rollup.py` | 确定性聚合：逐日表、完整度、汇总统计、趋势对比、相关性 |
| 置信度体系 | `measured` / `estimated` / `corrected` 三级标注 |
| 建议台账 | 提出 → 判定标准 → 回填 → 结论，完整闭环 |
| 标签协议 | 11 个短标签覆盖录入、报告、修正、回填 |
| 四 Skill 分工 | 主入口管流程，三个专科管领域知识 |
| 媒体归档 | 饮食照片、训练视频按日期自动命名归档 |

---

## 优势

| | 说明 |
|---|---|
| **不绑平台** | 数据是纯 Markdown + YAML，GPT / Claude / GLM / 本地模型都能直接读，换模型零迁移成本 |
| **不绑 App** | 不依赖任何服务的图表、导出或订阅；数据在磁盘上，可 grep、可 diff、可 git |
| **数字可信** | 聚合、求和、均值、趋势全部由脚本计算，模型不做算术 |
| **闭环可追溯** | 每条建议都能追到「依据什么指标 → 观察多久 → 结果如何 → 保留还是废弃」 |
| **知道自己的数据可不可信** | 完整度报告 + 置信度标注，避免拿垃圾数据下结论 |
| **录入成本极低** | 微信发张图 + 几个字；日常基本不用打字 |
| **隐私本地** | 所有数据留在你自己的机器上，仓库本身不含任何个人数据 |

---

## 目录结构

    data/<category>/YYYY-MM-DD.md    唯一数据源，一天一文件
    media/diet  media/training  media/sleep    照片与视频
    daily/YYYY-MM-DD.md             日报
    reviews/YYYY-Www.md             周报
    reviews/advice-ledger.md        ★ 建议台账
    profile/profile.md              长期画像：目标、基线、约束
    scripts/new_day.py              生成当天模板
    scripts/rollup.py               确定性聚合

---

## 快速开始

    pip install pyyaml
    python scripts/new_day.py            # 生成今天六类空白模板
    python scripts/rollup.py --days 7    # 输出 7 天趋势表

然后让 AI 读 `AGENTS.md` 和 `data/`，开始录入。

---

## Skills

| Skill | 职责 |
|---|---|
| **life-ledger** | 主入口：录入、写文件、跑脚本、台账回填、日报周报 |
| **strength-coach** | 重量选择、动作要点、渐进超负荷、1RM 估算、保护与伤痛 |
| **sleep-doctor** | 睡眠指标判读、作息重建、CBT-I、就医边界 |
| **nutrition-doctor** | 宏量配比、热量缺口、补剂、减脂与保力量 |

life-ledger 管**数据与流程**，三个专科管**领域知识**。可以只装 life-ledger。

### 安装

    npx skills add SunFlowerUE/Personal-assistant@life-ledger
    npx skills add SunFlowerUE/Personal-assistant@strength-coach
    npx skills add SunFlowerUE/Personal-assistant@sleep-doctor
    npx skills add SunFlowerUE/Personal-assistant@nutrition-doctor

也可以 clone 后把对应目录拷进你的 skills 目录（Codex：`~/.codex/skills/`）。

---

## 微信 / WorkBuddy 接入（可选）

见 `docs/wechat-workbuddy-init.md`（初始化提示词）与 `docs/wechat-phrases.md`（短语速查）。
绑定后微信发消息 → 本地 WorkBuddy 执行 → 结果回传微信，数据落到本地 Markdown。

---

## 隐私

所有数据留在你自己的磁盘上，本仓库不含任何个人数据；
`profile/profile.md`、`data/`、`media/`、`daily/` 已在 `.gitignore` 中排除。

---

## 已知局限

- 照片估算热量单次误差 ±20-30%，只能判断**配比与趋势**，不能判断绝对值
- **体重是唯一能校准整条链的低成本高精度信号**（误差约 0.3 kg，是能量平衡的真实积分）
- 单条时间序列无对照，n < 14 天只能说「观察到」，不能说「证明」
- 不提供医疗诊断；涉及疾病、用药、持续性症状请就医

---

## 许可证

MIT © 2026 SunFlowerUE
