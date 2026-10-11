# life-ledger · 本地生活数据账本

把饮食、训练、睡眠、体重、工作、家庭六类数据落到**本地 Markdown**，由 AI 生成日报与周报，
核心是维持一条能自我修正的闭环：

    输入数据 → 生成建议 → 执行 → 观察结果 → 回填修正 → 更新建议

## 为什么是本地 Markdown

- **不绑平台**：任何模型（GPT / Claude / GLM / 本地模型）都能直接读，换模型零迁移成本
- **不绑 App**：数据在磁盘上，可 grep、可 diff、可 git，不依赖任何服务的图表和导出功能
- **frontmatter 存数值，正文存人话**：机器读字段算趋势，人读正文看上下文

## 三条设计原则

**1. 脚本做算术，AI 做判断。**
跨天聚合、求和、均值、趋势全部跑 `scripts/rollup.py`。模型不做算术——容易错且费 token。
模型只负责：解释成因、提建议、判数据质量。

**2. 建议必须进台账，且提出时就写死判定标准。**
`reviews/advice-ledger.md` 是核心。提了建议不回填结果，闭环就断了。
判定标准（什么变化算有效、观察窗口几天）**必须提建议时写，不允许事后编**。

**3. 没有记录就是没有数据。**
缺失字段一律写 `null`，禁止用人群均值填补，禁止编造测量值。
区分 `measured`（实测）/ `estimated`（推算）/ `corrected`（人工修正）。

## 目录结构

    data/<category>/YYYY-MM-DD.md    唯一数据源，一天一文件
      diet  training  sleep  body  work  family
    media/diet  media/training  media/sleep    照片与视频
    daily/YYYY-MM-DD.md             AI 生成的日报
    reviews/YYYY-Www.md             AI 生成的周报
    reviews/advice-ledger.md        ★ 建议台账
    profile/profile.md              长期画像：目标、基线、约束（个人数据，勿提交）
    scripts/new_day.py              生成当天空白模板（已存在则跳过）
    scripts/rollup.py               确定性聚合

## 快速开始

    pip install pyyaml
    python scripts/new_day.py            # 生成今天六类空白模板
    python scripts/rollup.py --days 7    # 输出 7 天趋势表

然后让 AI 读 `AGENTS.md` 和 `data/`，开始录入。

## Skills

| Skill | 职责 |
|---|---|
| **life-ledger** | 主入口：录入、写文件、跑脚本、台账回填、日报周报 |
| **strength-coach** | 重量选择、动作要点、渐进超负荷、1RM 估算、保护与伤痛 |
| **sleep-doctor** | 睡眠指标判读、作息重建、CBT-I、就医边界 |
| **nutrition-doctor** | 宏量配比、热量缺口、补剂、减脂与保力量 |

life-ledger 管**数据与流程**，三个专科管**领域知识**。可以只装 life-ledger。

安装：

    npx skills add SunFlowerUE/Personal-assistant@life-ledger
    npx skills add SunFlowerUE/Personal-assistant@strength-coach
    npx skills add SunFlowerUE/Personal-assistant@sleep-doctor
    npx skills add SunFlowerUE/Personal-assistant@nutrition-doctor

也可以 clone 后把对应目录拷进你的 skills 目录（Codex：`~/.codex/skills/`）。

## 微信 / WorkBuddy 接入（可选）

想用手机随手录入时，见 `docs/wechat-workbuddy-init.md`（初始化提示词）
和 `docs/wechat-phrases.md`（日常短语速查）。核心是一套极短标签语法：

    [睡眠] + 截图      [饮食] 早餐 08:30 + 照片
    [训练] 卧推 60kg 8x3        [体重] 70.2
    [日报]  [周报]  [趋势] 近30天  [修正]  [回填]

## 隐私

所有数据留在你自己的磁盘上，本仓库不含任何个人数据；
`profile/profile.md`、`data/`、`media/`、`daily/` 已在 `.gitignore` 中排除。
**发布前请自查没有把个人数据提交上去。**

## 已知局限

- 照片估算热量单次误差 ±20-30%，只能判断**配比与趋势**，不能判断绝对值
- **体重是唯一能校准整条链的低成本高精度信号**（误差约 0.3 kg，是能量平衡的真实积分）
- 单条时间序列无对照，n < 14 天只能说"观察到"，不能说"证明"
- 本仓库不提供医疗诊断；涉及疾病、用药、持续性症状请就医

## 许可证

MIT。
