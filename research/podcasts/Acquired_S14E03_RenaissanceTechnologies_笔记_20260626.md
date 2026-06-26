# Acquired S14E03 · Renaissance Technologies 笔记

> **原始视频：** YouTube `2KjW4BqNFy0`（Acquired 频道，"Renaissance Technologies (Audio)"）
> **时长：** 3 小时 08 分 · **集数：** Season 14, Episode 3
> **原始 transcript：** 278 段，存于同目录 `Acquired_S14E03_RenaissanceTechnologies_transcript_20260626.txt`
> **来源播客源：** Ben Gilbert & David Rosenthal，引用 Greg Zuckerman《The Man Who Solved the Market》为底层文献
> **笔记日期：** 2026-06-26

---

## 🎯 一句话总结

文艺复兴科技 / Medallion Fund 是人类金融史上最赚钱的投资工具——**34 年（1988–2022）毛年化 66%、净年化 39%**（扣 5% 管理费 + 最高 44% 业绩分成后），累计业绩分成约 $60B。秘诀不是更快的电脑或更好的数据，而是 **"单一模型 + 学术文化 + LP/GP 内循环 + 信号处理哲学"** 这一整套无法复制的组织设计。

---

## 📅 时间线（25 年从一篇论文到一台印钞机）

| 年份 | 事件 | 关键人物 |
|------|------|----------|
| 1938 | Jim Simons 出生，Newton, MA | Jim |
| 1958–61 | MIT 本科 + 硕士（数学） | Jim |
| 1961 | 与陈省身合作（→Chern–Simons 理论，弦论基础） | Jim, Chern |
| 1964 | **IDA 论文**：将"信号处理"用于市场预测 | Jim, Lenny Baum |
| 1967 | 写纽约时报反越战文章，被五角大楼开除 | Jim |
| 1968 | Stony Brook 数学系主任，无限预算招人 | Jim |
| 1978 | 离开学术界，创立 **Monometrics** | Jim, Lenny Baum |
| 1982 | Monometrics + Howard Morgan 私投 → 改名 **Renaissance Technologies** | Jim, Howard |
| 1984 | Lenny Baum 政府债长仓爆雷 -40%，触发条款离场 | — |
| 1985 | James Axe + Sandor Strauss 移到加州创立 **Axcom** | Axe, Strauss |
| 1988 | Howard 拆出风投（→ First Round Capital），**Medallion Fund** 启动 | — |
| 1989 | Strauss 抓 tick 数据 + 早期 1900s 历史数据 → ETL 雏形 | Strauss |
| 1990 | Berlekamp 提"高频小额 + Kelly 仓位"思路；1990 净 +55% | Berlekamp |
| 1993 | **关基金**（不再接受新 LP）；IBM 招来 **Peter Brown + Bob Mercer + David Magerman** | Peter, Bob |
| 1994 | 进入**股票**市场；当年毛 +93% | — |
| 2000 | 科技泡沫破，年毛 **+128% / 净 +98.5%**，AUM $1.9B → $3.8B（纯复利，无新钱） | — |
| 2002 | 用 **basket options** 加杠杆：$1 现金撬 $12.5 名义头寸，高峰 $20 | — |
| 2003 | **踢走所有外部 LP**，Medallion 变员工内部基金；推出 RIEF 机构基金 | — |
| 2007 | 毛 **+136%** | — |
| 2008 | 毛 **+152%**（金融海啸别人死，他们赚翻） | — |
| 2009 | Jim 退休，Peter & Bob 任联席 CEO | — |
| 2017 | Jim 让 Bob 卸任联席 CEO（因政治捐款争议），Bob 留任科学家 | — |
| 2020 | 毛 +149% / 净 +76% | — |
| 2022 | Jim Simons 离世（2024-05），净资产 ~$30B | — |

> **关键洞察：1964 论文 → 1990 真正赚钱，间隔 25 年。** 这不是创业神话里的"两年十亿倍"，是慢科学。

---

## 🧬 二、Medallion 为何不可复制（三块拼图）

Acquired 用"tapestry"形容这套机制——三块织在一起才成布：

### 1️⃣ 单一模型架构（One Model）
- **所有市场（股票/外汇/商品/期货）共用一个模型**
- 整个公司只有一个 code base，**全员可见全代码**
- 你改的代码，隔壁同事的策略自动受益
- 别人（CITADEL / 2 Sigma / DE Shaw）都是多策略多团队、互相竞争
- Bob Mercer 原话：「We're right 50.75% of the time. We're 100% right 50.75% of the time.」

### 2️⃣ 极致小团队 + 学术天堂文化
- 总员工 < 400 人，研究/工程 ~150–200 人（对手 2000–5000 人）
- 中位任期 **16 年**（LinkedIn 数据）
- Long Island East Setauket 偏僻小镇，"学院派没有学生"
- **终生 NDA + 5 年非竞**（NY 法律限制），但**真正锁住人的是经济+社会+法律三层**
- 大多数研究员**不会读资产负债表**，纯信号处理
- 招人不看金融背景："easier to teach smart people the investing business than teach investing people how to be smart"

### 3️⃣ LP/GP 同源 + 价值转移机制（最聪明的设计）
- 所有人都是 Medallion 的 LP，员工逐渐变成"毕业生 = 老 LP"
- 维持 **5% 管理费 + 44% 业绩分成**（业内最高）
- 这不是为了赚钱，**是为了把每年的经济回报从"老人"转移给"新人"**
- 防止新人攒够钱出走单干（他们看过整个 code base）
- 401k 计划本身就是 Medallion 基金（专门起诉过政府拿到豁免）
- 类比：**像大学的终身教职体系**——年轻教师讲席拿大头，老教授转成"出资方"

---

## 📊 三、关键数字（全网最完整的硬数据）

| 指标 | 数据 | 备注 |
|------|------|------|
| Medallion 毛年化（1988–2022） | **66%** | Greg Zuckerman 整理，业内引用基准 |
| Medallion 净年化（扣费后） | **39%** | 同期 |
| 总业绩分成 | **$60B** | 整段历史累计 |
| 估算 Jim 个人净资产 | ~$30B | 约占 RenTech 一半 |
| 当前 Medallion 规模 | $10–15B | slippage 限制 |
| 机构基金 RIEF 规模 | $60–70B（峰值 $100B+） | 给外部 LP |
| Jim 任期（1988–2009） | 毛 63.5% / 净 40.1% | — |
| Peter & Bob 任期（2010–2022） | 毛 77.3% / 净 40.3% | 高费率下仍跑赢 Jim 时代 |
| 2008 危机 | 毛 **+152%** | 市场崩，他们大赚 |
| 2007 危机 | 毛 **+136%** | 同上 |
| 2000 互联网泡沫 | 毛 **+128%** | — |
| 2020 疫情 | 毛 +149% / 净 +76% | — |
| 历史最高 Sharpe | **7.5**（2004） | 对比 S&P 500 约 0.4 |
| 杠杆（basket options） | 现金 $1 → 名义头寸 $12.5，峰值 $20 | 2002 IRS 补税案：$6.8B |
| Jim 个人 IRS 补税 | **$670M** | basket options 长资本利得被否定 |
| 旗下 90 个 PhD | 数学/物理/CS | 官网公开 |
| 算力 | 50,000 核 + 150 Gbps 网络 + 每天 40 TB 新数据 | — |
| 代码量 | 1000 万+ 行 | 没人能 hold 整盘 |
| 交易频次 | 15–30 万笔/天 | 不是 HFT，"slow + smart" 象限 |
| 平均持仓 | 1–2 天 | Medallion |
| 13F 持仓数 | 4300+ 只股票 | 极度分散 |

---

## 🧠 四、为什么能赚钱（机制层面）

### 核心：**信号处理哲学**
- 不关心标的本身，不看基本面
- 当作 HMM（隐马尔可夫模型）：状态 → 概率分布 → 下一状态
- 同样的数学在 1960s 用于破苏联密码
- 同样的数学在 2020s 用于 ChatGPT
- **Peter Brown 的博导就是 Geoffrey Hinton**（Ilya Sutskever 也是 Hinton 学生）

### 三个杠杆叠加：
1. **数据**（30+ 年清洗的 1900s 至今的干净 tick + 历史数据，Strauss 的执念）
2. **算力**（50k 核 + 每秒 150 Gbps）
3. **算法**（机器学习发现**人脑根本想不到的关系**）

### 几个反直觉的事实：
- **持仓 1–2 天**——不是 HFT，"slow + smart" 象限，不是 "Flash Boys"
- **高波动期最赚钱**——别人 panic sell 时，他们在捡血筹码
- **对手是散户 + 恐惧的共同基金**，不是其他 quant
- **risk-on 时反而要慎重**（2000 泡沫 Peter Brown 想全押模型，Jim 强行减仓）

### 跟其他 quant 的本质区别：
- **其他 quant**：人给 idea → 机器验证 → 人拍板下注
- **RenTech**：机器给 idea → 机器验证 → 机器下注，**人只负责维护模型**

---

## ⚖️ 五、Seven Powers 套用（Acquired 的标准分析框架）

| Power | RenTech 是否适用 | 说明 |
|-------|-----------------|------|
| 规模经济 | ❌ **反规模** | slippage 限制规模，$10–15B 是天花板 |
| 网络经济 | ❌ | 不跟任何人说话 |
| 切换成本 | ❌ | — |
| 品牌 | ⚠️ 仅 RIEF 用得到 | Medallion 不接受新钱 |
| 反定位 | ⚠️ 部分 | 单一模型 vs 多策略；零外部 LP vs 全行业接钱 |
| 流程优势 | ✅ **核心** | 30 年叠加的 code + 流程 + 协作机制 |
| 锁定资源 | ✅ **核心** | 干净数据 + PhD 池 + 极度保密 |

**结论：流程优势 + 锁定资源**——这不是某单个技巧，是 30 年慢慢磨出来的复利。

---

## 💰 六、对我们的启示（库哥视角）

### 直接投资层面
1. **完全投不进去**——Medallion 已 23 年不接外部资金，存量 GP/LP 都是内部人
2. **RIEF 能投但不值得追**——费后表现就是 S&P 500 水平，预期收益 ~8%
3. **学不到 RenTech**——人才/数据/文化/年限四样缺一不可，AUM 越大越学不来

### 思想层面（这部分才是真正值得吸收的）
1. **小团队 + 共享基础设施 > 大团队 + 竞争**
   - 我们做研究、写代码、做产品时，"一个 code base 全员可见"是稀缺优势
2. **价值转移机制是高激励的正解**
   - 老员工有钱后必然躺平，新人必然想出走；RenTech 用 44% carry 把"压岁钱"从老人转给新人，比传统奖金更精确
3. **"让模型做决策" 比 "让人拍板" 更靠谱**
   - 任何容易情绪化的判断（择时、panic sell、追涨杀跌）都是 RenTech 的 alpha 来源
4. **隐秘的 alpha = 非直觉的关系**
   - Tesla 与小麦期货同涨，原因是某 hedge fund 同时持有两者做再平衡——人脑永远找不到这种关系
5. **不追求"聪明地预测"，追求"高胜率 + 无数次下注 + Kelly 仓位"**
   - 50.75% 胜率，10 万次下注，足够造富
   - 这条对个人交易也有指导意义
6. **慢科学值得等**
   - 25 年才赚钱。中本聪至今没现身；很多真正伟大的事都不是 18 个月跑出来的

### 可能的"抄作业"启发
- 想做一家"小而美"的量化基金？门槛极高（人才 + 数据 + 15 年磨合）
- 想学他们的"组合管理"哲学？把"信号处理"思想用到我们自己的决策上——把每个判断拆成"可量化的状态 → 概率分布"
- 想研究具体可学的方法论？重点看 **hidden Markov model** 和 **Kelly criterion**

---

## ⚠️ 七、熊市视角（Acquired 自己列的）

- 科技巨头（LLM 时代）让 quant 工具平民化，可能拉平 RenTech 优势
- 真正人才可能外流（同领域开源工具多了，"离开 RenTech" 不再等于"放弃一切"）
- 文化稀释：Jim 去世、Mercer 退出，灵魂人物减少
- 新任联席 CEO David Lippe（管机构基金出身）——纯 Medallion 派是否被稀释是悬念
- 模型每两年完整重构——万一失去一个关键研究员，"整个系统没人能 hold 在脑中" 的风险

> **核心讽刺：** RenTech 自己可能就是 alpha 的来源。"复杂的自适应系统" 被他们摸透的同时，他们的存在本身也在改变系统本身。

---

## 🎙️ 八、其他亮点（金句 / 八卦）

- **"You can't spell Renaissance without AI"**——开场双关
- Peter Brown 2000 年泡沫时想辞职，Jim 说"经历过这个的人更值钱"
- Jim 退休前给 Peter 的金句："你敢激进是因为我在旁边挡你。等你坐到这把椅子，你自己就会保守了"——人类互动的反身性洞见
- Lenny Baum 1984 年政府债长仓爆雷触发"合伙人条款"被强制清仓离场——**他们也是吃过亏的**
- Jim Simons 退休后给自家 family office 打电话问"市场大跌怎么办"——**Jim 也是 Jim，不是神**
- First Round Capital Fund 1（$125M）回报 50×，含 Roblox/Uber/Square——Jim 当 LP 赚的可能跟 Howard 当 RenTech LP 赚的一样多
- **插曲八卦：** Bob Mercer 出钱搞了 Breitbart + Cambridge Analytica + 2016 Trump + Brexit；Jim Simons 同期是大额民主党捐款人。两人至今同公司同事，"美式不可思议"

---

## 🔍 九、信息源建议（库哥想深挖）

1. **必读：** Greg Zuckerman《The Man Who Solved the Market》（唯一一本专题书）
2. **次选：** Scott Patterson《The Quants》（2011，2 章 RenTech）
3. **一手资料：** Peter Brown 在 GS Exchanges 的访谈（YouTube 有）
4. **一手资料：** Peter Brown 关于 basket options 的国会证词
5. **Bloomberg 2016 那篇 RenTech 报道**——Acquired 评 "早期唯一一篇像样的"

---

## 🧾 十、本次工作记录

- **数据来源：** YouTube `2KjW4BqNFy0` → podscripts.co 完整 transcript（278 段，0–3h05m）
- **失败路径：** yt-dlp 反爬被 ban；youtube-transcript-api 无字幕；subeasy.ai 仅到 1h58m
- **本地存档：** `research/podcasts/Acquired_S14E03_RenaissanceTechnologies_transcript_20260626.txt`
- **笔记版本：** v1，2026-06-26