# Tech Learning - 技术学习笔记

> 库哥的 LLM / AI 系统性学习笔记仓库。
> 从「使用 AI」到「理解 AI」的学习路径沉淀。
> **创建日期：** 2026-06-05

## 📚 学习路径

| 阶段 | 主题 | 状态 | 文档 |
|------|------|------|------|
| 1️⃣ | Transformer 直觉 | ✅ 完成 | [The Illustrated Transformer 中文翻译](./illustrated-transformer_中文翻译.md) |
| 2️⃣ | Transformer 7 年演进 | 🔄 进行中 | [LLM-book Ch.3 中文翻译](./llm-book-ch3-transformer-evolution_中文翻译.md) |
| 3️⃣ | Annotated Transformer (论文+PyTorch) | ⏳ 待开始 | — |
| 4️⃣ | Multi-Query Attention 深入 | ⏳ 待开始 | — |
| 5️⃣ | RoPE 旋转位置编码深入 | ⏳ 待开始 | — |
| 6️⃣ | 视频课程 (MIT 6.S898 / Stanford CS224N) | ⏳ 待开始 | — |

## 📖 已有文档

### 1. The Illustrated Transformer 中文翻译
- **作者：** Jay Alammar
- **原文：** https://jalammar.github.io/illustrated-transformer/
- **翻译日期：** 2026-06-05
- **核心内容：**
  - 6 大核心概念速查表
  - 关键公式：`Attention(Q, K, V) = softmax(QK^T / √d_k) V`
  - 配图说明 + 学习路径建议
- **适合人群：** LLM 入门者必读

## 🎯 学习方法

1. **每读完一篇 → 整理成 Markdown 推到本目录**
2. **每篇结尾附「🎓 库哥导读」**（核心要点 + 学习路径）
3. **双端同步 GitHub (master) + Gitee (main)**

## 🛠️ 工具栈

- 翻译：MiniMax-M3 (本 AI)
- 原文抓取：web_fetch
- 推送：git + SSH
- 排版：emoji + 项目符号（Telegram 友好）

---

*最后更新：2026-06-05*
