# AI News Digest — 每日 AI 产业情报

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://claude.ai/code)

一个 Claude Code Skill，每天帮你搜索全网 AI 行业资讯，按多维评分体系筛选，对高价值新闻进行深度分析（含历史类似事件对照），最终生成精美的 HTML 邮件发送到你的邮箱。

## 功能特性

- **全网中英文搜索** — 覆盖融资并购、芯片半导体、数据中心、能源电力、AI应用、政策监管、公司动态 7 大分类
- **多维加权评分** — 5 维度评分（资金信号 35%、产业链影响 25%、政策监管 20%、时效稀缺 12%、来源权威 8%），可配置阈值
- **二级分析体系** — 高分条目（≥7.5）进入深度分析，200-300 字 + 历史类似事件对照 + 投资含义；中等分条目 100 字简报
- **历史对照** — 对重大事件搜索历史上的类似案例，对比异同，作为投资参考
- **HTML 邮件投递** — 通过 Brevo SMTP 发送精美排版邮件（免费 300 封/天）
- **完全可配置** — 评分权重、搜索关键词、邮件外观、配色字体全部通过 YAML 文件控制

## 快速开始

### 1. 安装 Skill

下载 `.skill` 文件到本地，或克隆本仓库到 `~/.claude/skills/ainewsdigest/`：

```bash
git clone https://github.com/LUJUNRU123456/ainewsdigest.git ~/.claude/skills/ainewsdigest/
```

### 2. 配置邮件

编辑 `mail_config.yaml`，填入你的 Brevo SMTP 信息：

1. 在 [app.brevo.com](https://app.brevo.com) 注册（免费，无需绑卡）
2. 完成发件邮箱验证
3. 在 SMTP & API → SMTP Keys 生成密钥，记下 SMTP Login
4. 编辑 `mail_config.yaml` 中的 `username`、`sender_email`、`recipients`
5. 将 SMTP 密钥设为环境变量 `EMAIL_PASSWORD`（推荐写入 `~/.claude/settings.json` 的 `env` 字段）

### 3. 触发使用

在 Claude Code 中输入以下任一触发词：

- `AI日报`
- `来一份AI日报`
- `今天有什么AI新闻`
- `AI情报`
- `看看最近的AI动态`
- `ainews` / `ai news digest`

也可以随口问「今天AI圈有什么大事？」——skill 会自动触发。

## 配置后门

所有配置都在 YAML 文件中，每行都有中文注释：

| 文件 | 控制内容 |
|------|---------|
| `scoring_config.yaml` | 评分维度、权重、阈值、硬性规则 |
| `sources_config.yaml` | 搜索关键词、RSS 源、排除词 |
| `mail_config.yaml` | SMTP 服务器、收件人、邮件配色/字体/排版 |

改配色：编辑 `mail_config.yaml` 的 `style.colors` 段
改阈值：编辑 `scoring_config.yaml` 的 `thresholds` 段
加信源：编辑 `sources_config.yaml` 的 `rss_feeds` 段

## 评分模型

| 维度 | 权重 | 说明 |
|------|------|------|
| 资金信号强度 | 35% | 涉及金额、估值变化、融资轮次 |
| 产业链影响半径 | 25% | 影响的上下游环节数量和深度 |
| 政策监管冲击 | 20% | 政策变化的力度和紧急程度 |
| 时效与稀缺性 | 12% | 新闻的新鲜度和独家性 |
| 来源权威度 | 8% | 来源的可信度和专业程度 |

- **≥7.5 分** → 深度分析（含历史对照）
- **4.0–7.4 分** → 简报摘要
- **<4.0 分** → 丢弃

## 文件结构

```
ainewsdigest/
├── SKILL.md              # Skill 主文件（工作流定义）
├── scoring_config.yaml   # 评分配置
├── sources_config.yaml   # 搜索源配置
├── mail_config.yaml      # 邮件配置（视觉风格后门）
└── scripts/
    └── send_email.py     # Brevo SMTP 发送脚本
```

## 演示效果

邮件包含「今日重点关注」深度分析区和「其他值得关注」简报区，每条深度分析附带产业链影响传导路径和历史对照框。

## 许可

MIT License — 自由使用、修改、分发。

## 免责声明

本工具生成的内容包含投资分析，仅供研究参考，不构成投资建议。使用者需自行判断投资风险。
