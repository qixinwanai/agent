# 通用型 AI 工作流助手

一个基于 Streamlit + OpenAI API 的通用型多 Agent 工作流助手，可用于资料整理、文档分析、任务规划、会议复盘和内容生成。

## 功能

- 资料收集 Agent
- 阅读理解 Agent
- 结构化整理 Agent
- 任务规划 Agent
- 内容生成 Agent
- 支持完整工作流运行
- 支持单 Agent 模式
- 支持导出 Markdown 报告

## 安装

```bash
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env`，并填写你的 API Key：

```bash
cp .env.example .env
```

`.env` 示例：

```txt
OPENAI_API_KEY=你的_API_Key
OPENAI_MODEL=gpt-4o-mini
```

## 运行

```bash
streamlit run app.py
```

## 适用场景

- 学习总结
- 办公提效
- 项目策划
- 文档分析
- 会议复盘
- 内容创作

## 项目说明

本项目实现了一个通用型 AI 工作流助手，包含资料收集、阅读理解、结构化整理、任务规划和内容生成五个 Agent，可围绕用户输入的复杂目标自动完成信息分析、任务拆解和报告生成。该系统需要处理长文本、多轮推理和多 Agent 协作，因此适合用于展示 AI 工作流对 token 消耗和实际效率提升的需求。
