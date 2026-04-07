# MEMORY.md - 长期记忆

> 更新日期：2026-04-06

## 用户信息
- **Name:** 库哥
- **称呼:** 库哥
- **时区:** Asia/Shanghai (GMT+8)
- **首次对话:** 2026-04-01
- **备注:** 甜辣是库哥的妻子

## IM 渠道与称呼对照
| 渠道 | 平台 | 称呼 | open_id |
|---|---|---|---|
| 飞书 | Feishu | 库哥 | ou_c63b2d782af0cbc539a5895a4a424069 |
| 微信（账号1） | WeChat | 库哥 | _(待补充)_ |
| 微信（账号2） | WeChat | 甜辣 | _(待补充)_ |

## ⚠️ 记忆跨渠道互通
库哥同时使用飞书和微信与我沟通。**两边记忆互通**，所有对话内容都存在 MEMORY.md 和 memory/ 日期文件中。
无论哪个渠道，都要先查记忆文件再作答，确保上下文衔接。

## 用户偏好
- 默认使用 Interactive Brokers (IB Gateway) 查询账户
- 习惯用中文交流

## 重要任务/要求
- 要求股票分析报告上传到 Gitee（需要用户提供仓库信息）

## IBKR 配置
- Docker + IB Gateway 已部署在 /root/ibkr-gateway/
- 账户: wintermelon27agent, 账户ID: U12801920
- 连接端口: 4003
- 当前状态: Read-Only（账户无交易权限）

## 代码托管
- **Gitee:** https://gitee.com/wintermeloncurry/agent_research (main/research/stocks) ✅
- **GitHub:** https://github.com/wintermelon27/agent_research (master/research/stocks) ✅
- SSH keys: `id_ed25519` (Gitee), `id_ed25519_github` (GitHub)
- GitHub SSH key: openclaw-agent

## 任务记录
- OKLO 研究报告已上传至 Gitee ✅

## 代码托管配置

### SSH Keys
- `~/.ssh/id_ed25519_github` → GitHub（在 ssh config 中配置 Host github.com）
- `~/.ssh/id_ed25519` → 预留（Gitee 目前使用 HTTPS+Token，无需 SSH key）

### Remote 仓库
| 名称 | 协议 | 地址 | 分支 |
|---|---|---|---|
| `origin` | SSH | `git@github.com:wintermelon27/agent_research.git` | master |
| `gitee` | HTTPS (带token) | `https://gitee.com/wintermeloncurry/agent_research.git` | main |

### 仓库本地路径
`/root/.openclaw/workspace` — 当前 workspace 即为 git 仓库根目录

### Git 用户信息
- name: Ku's Jarvis
- email: openclaw@server.local

### 注意
- Gitee remote URL 中硬编码了 token（`b5dcb451ba76c18f91927fcf7ff148a0`），push 时无需输入密码
- 后续提交优先推送到 origin (GitHub) 和 gitee (Gitee)

## 研究报告要求（2026-04-07 记录）

**覆盖范围：** 股票、ETF、基金、期权、期货、金融衍生品等

**分析维度：**
1. 最新财报数据
2. 基本面分析
3. 增长空间
4. 近期业绩透露
5. 技术面分析
6. 产品动向
7. 竞争对手动向
8. 面临的问题/风险
9. 未来重要事件
10. 近期新闻
11. 专业机构动向和评级
12. 达人/游资/专业研究员分析

**输出格式：** Markdown

## 教训
- 每次对话结束要把用户的重要信息写入 memory/ 日期文件或 MEMORY.md
- session transcript 是辅助记忆，但主要还是要主动写 memory，不能完全依赖它
