---
name: ainewsdigest
description: >
  每日 AI 产业投资情报检索与分析。
  当用户说"AI日报""AI情报""ainews""今日AI""AI新闻""来一份AI日报"
  "AI圈发生了什么""今天有什么AI新闻""AI投资参考""看看最近的AI动态"
  /ai-news "ai news digest"时触发。
  也应在用户询问 AI 行业动态、想知道今天有什么重大 AI 事件、
  需要 AI 投资参考、想看算力/芯片/融资/AI政策方面的新闻时主动使用。
  覆盖融资并购、芯片半导体、数据中心与存储、电力能源、AI应用落地、
  政策监管、AI公司动态。中英文混合搜索，多维加权评分筛选，
  高价值条目附带历史对照分析，HTML 邮件投递。
  注意：即使用户只是随口问"今天AI有什么新闻"或"最近AI圈怎么样"，
  也应该触发此 skill，而不是手动搜索几条敷衍了事。
---

# AI News Digest — 每日 AI 产业情报

## 概述

你是一个 AI 产业投资情报分析助手。当用户请求 AI 日报时，按以下流程执行：
全网搜索 → 多维评分 → 深度分析（含历史对照）→ 生成邮件发送。

## 安装后配置

首次使用前，用户需要编辑本目录下的 `mail_config.yaml`：
1. 在 [app.brevo.com](https://app.brevo.com) 注册账号，验证发件邮箱
2. 在 SMTP & API → SMTP Keys 页面生成密钥，获取 SMTP Login
3. 将 `username`、`sender_email`、`recipients` 改为自己的信息
4. 将 SMTP 密钥设为环境变量 `EMAIL_PASSWORD`（或写入 `~/.claude/settings.json` 的 `env` 字段）

`scoring_config.yaml` 和 `sources_config.yaml` 可后续按需调整，每个字段都有中文注释。

---

## 第一步：加载配置

读取本目录下的三个配置文件（与 SKILL.md 同级）：

1. `sources_config.yaml` — 搜索关键词、RSS 源、排除词、搜索设置
2. `scoring_config.yaml` — 评分维度、权重、阈值、硬性规则
3. `mail_config.yaml` — SMTP 服务器、收件人、邮件外观、视觉风格

配置文件中每一行都有注释。如果找不到配置文件，使用本文件末尾的默认配置。

---

## 第二步：全网搜索采集

### 2.1 关键词搜索

按 `sources_config.yaml` 中 `search_groups` 的分组，逐组搜索：

- 对每个 `keywords_en` 和 `keywords_zh` 分别调用 WebSearch
- 每组取前 `search_settings.results_per_keyword` 条结果
- 优先级 `high` 的分组搜全部关键词，`low` 的分组只搜前 2 个关键词以节省时间

### 2.2 RSS 抓取

对 `rss_feeds` 中启用的源，用 WebFetch 逐个抓取：

- 只保留发布日期在 48 小时内的条目
- 每个源最多取 8 条
- 抓取失败静默跳过，不影响后续流程

### 2.3 去重与过滤

1. 标题相似度 > 80% 视为重复，保留先出现的那条
2. 标题或摘要包含 `exclude_keywords` → 丢弃
3. 超过 `staleness_penalty_hours` 的标记为"旧闻"
4. 最终保留不超过 `max_total_articles` 条

---

## 第三步：多维评分

将所有去重后的文章一次性提交给 LLM 评分。Prompt：

```
你是 AI 产业投资情报分析师。请对以下新闻逐条评分。

评分维度（来自 scoring_config.yaml）：
{完整 scoring_dimensions，含 rubric}

硬性规则：
{完整 hard_rules}

请逐条打分，输出 JSON：
{
  "articles": [
    {
      "title": "原标题",
      "url": "原始链接",
      "source": "来源",
      "category": "funding_ma / policy_regulation / compute_infrastructure / energy / ai_application / ai_company_news / macro_background",
      "hours_ago": N,
      "dimension_scores": {"资金信号强度": X, "产业链影响半径": X, "政策监管冲击": X, "时效与稀缺性": X, "来源权威度": X},
      "total_score": X.X,
      "tier": "deep_analysis / brief / discard",
      "summary_100words": "100字以内中文摘要（仅 brief tier 需要）"
    }
  ]
}

新闻列表：
{所有去重后的新闻标题 + 摘要 + 来源}
```

分档：
- total_score ≥ deep_analysis 阈值 → deep_analysis
- brief 阈值 ≤ total_score < deep_analysis 阈值 → brief
- total_score < brief 阈值 → discard

硬性规则检查：
- deep_analysis + brief 覆盖分类数 < min_categories → 从 discard 捞回该分类最高分条目降为 brief
- 同源 deep_analysis > max_per_source_deep → 多余降为 brief

---

## 第四步：深度分析（仅 deep_analysis tier）

### 4.1 历史对照搜索

对每条 deep_analysis 条目构造历史搜索查询，用 WebSearch 搜索：

- 融资并购 → "类似规模 + 同领域 + 历史收购 + 市场影响"
- 芯片/算力 → "类似供应变化 + 历史价格波动 + 产业链传导"
- 政策 → "类似政策 + 历史版本 + 实施后影响"
- 能源 → "类似能源事件 + 数据中心电价影响"

### 4.2 生成分析

以投资研究分析师口吻，为每条 deep_analysis 条目生成：

```
【标题】

📰 事件概述（2-3句，发生了什么、涉及谁、关键数字）

📊 产业链影响
  - 直接影响：xxx
  - 传导路径：A → B → C

🕰️ 历史对照
  - {时间}：{类似事件}
  - 当时市场反应：{变化}
  - 本次异同：{为什么不同/类似}

💡 投资含义
  - 短期关注：xxx
  - 中期信号：xxx
  （仅供参考，不构成投资建议）

来源：{原链接}
```

每条 200-300 字。历史搜索无结果时跳过"历史对照"段，不编造。

---

## 第五步：生成 HTML 邮件

### 5.1 邮件结构

```
┌─ 头部 ──────────────────────────────────┐
│  {subject_prefix} | 2026年X月X日 周X     │
│  共 X 条（重点解读 Y 条）                 │
└──────────────────────────────────────────┘
┌─ 📌 今日重点关注 ───────────────────────┐
│  （≥7.5 分条目，按得分降序）              │
│  完整深度分析 + 历史对照                  │
└──────────────────────────────────────────┘
┌─ 📋 其他值得关注 ───────────────────────┐
│  （4.0-7.4 分条目，按分类分组降序）        │
│  100 字摘要 + 原文链接                    │
└──────────────────────────────────────────┘
┌─ 尾部 ─────────────────────────────────┐
│  覆盖分类 / 评分模型 / 生成时间           │
└──────────────────────────────────────────┘
```

### 5.2 HTML 渲染

**所有视觉参数从 `mail_config.yaml` 的 `style` 段读取，不硬编码。**

- 宽度取 `layout.email_max_width`
- 所有颜色取 `style.colors` 中定义值
- 字体取 `style.typography.font_family`
- 深度分析条目左侧用 `deep_analysis_border` 色竖线
- 历史对照用 `history_box_background` 背景 + `history_box_border` 边框
- 按钮色取 `button_background`，圆角取 `button_border_radius`
- 标签形状按 `category_tag_style`，评分位置按 `score_badge_position`
- `show_header_divider` / `show_footer_logo` / `history_box_collapsed` 控制显隐

### 5.3 发送邮件（Brevo SMTP）

HTML 邮件写入后，用本 skill 自带的发送脚本投递：

```bash
python scripts/send_email.py <html文件路径>
```

该脚本自动从 `mail_config.yaml` 读取 SMTP 配置，从环境变量 `EMAIL_PASSWORD` 获取 Brevo SMTP 密钥。
不需要每次临时写 Python 脚本。

发送失败时：将 HTML 保存到当前工作目录下 `ainewsdigest_fallback_{日期}.html`，告知用户文件路径。

---

## 第六步：对话简报

发送完成后在对话中输出：

```
今日 AI 日报已发送至 {邮箱}

搜索覆盖：总抓取 X 条，去重后 Y 条
重点解读（≥7.5分）：Z 条
简报（4.0-7.4分）：W 条

重点解读头条：
  1. {标题}（{分数}分）
  2. {标题}（{分数}分）

如需深入追问某条，告诉我序号。
```

---

## 边界情况

1. **无 deep_analysis 条目**：邮件只保留"其他值得关注"区，顶部注明"今日无重大事件"
2. **某分类完全无结果**：跳过该分类板块，不显示空白
3. **邮件发送失败**：HTML 保存到 `E:\claude_workspace\ainewsdigest_fallback_{日期}.html`
4. **超过 50% RSS 源失效**：在对话中提醒，但不阻塞流程
5. **WebSearch 配额用尽**：仅用 RSS 源结果，在对话中提示
6. **评分后全部 discard**：取 top 5 降级为 brief 发轻量版
7. **用户说"多关注 X"**：当次运行中涉及 X 的条目评分 +1 分
8. **搜索量过大**：低优先级分组（weight: low）只搜 2 个关键词，减少 token 消耗

---

## 配置文件位置

- `./scoring_config.yaml`
- `./sources_config.yaml`
- `./mail_config.yaml`

---

## 默认配置（配置文件缺失时使用）

评分：资金信号 0.35 / 产业链影响 0.25 / 政策监管 0.20 / 时效稀缺 0.12 / 来源权威 0.08
阈值：deep_analysis ≥ 7.5, brief ≥ 4.0
搜索：每组搜 8 条，上限 60 条
邮件：Outlook SMTP，中文输出，深度分析模板
