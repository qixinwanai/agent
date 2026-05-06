"""
通用型 AI 工作流助手 - 单文件可运行版

功能：
1. 多 Agent 协作：资料收集、阅读理解、结构化整理、任务规划、内容生成
2. 支持输入主题、长文本、会议记录、报告内容等
3. 支持一键生成完整工作流结果
4. 支持单独运行某个 Agent
5. 支持导出 Markdown 报告

运行方式：
1. pip install -r requirements.txt
2. 新建 .env 文件，写入：OPENAI_API_KEY=你的 API Key
3. streamlit run app.py

说明：
- 本代码使用 OpenAI Chat Completions 接口。
- 如果你使用其他模型服务，只需要替换 call_llm() 函数即可。
"""

import os
import time
from datetime import datetime
from typing import Dict

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.4,
    max_retries: int = 3,
) -> str:
    """统一的大模型调用函数。"""
    if client is None:
        return "错误：未检测到 OPENAI_API_KEY。请在 .env 文件中配置 OPENAI_API_KEY。"

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))

    return f"模型调用失败：{last_error}"


class Agent:
    """基础 Agent 类。"""

    def __init__(self, name: str, role: str, goal: str, output_format: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.output_format = output_format

    def build_system_prompt(self) -> str:
        return f"""
你是一个专业的 AI 工作流助手中的子 Agent。

你的名称：{self.name}
你的角色：{self.role}
你的目标：{self.goal}

要求：
1. 输出必须清晰、结构化、可执行。
2. 不要编造事实；如果信息不足，请明确指出。
3. 优先给出可落地的结果，而不是空泛建议。
4. 使用中文回答。
5. 按照指定格式输出。

输出格式：
{self.output_format}
""".strip()

    def run(self, task: str, context: str, model: str, temperature: float = 0.4) -> str:
        user_prompt = f"""
当前用户任务：
{task}

上下文材料：
{context}

请根据你的角色完成任务。
""".strip()
        return call_llm(
            system_prompt=self.build_system_prompt(),
            user_prompt=user_prompt,
            model=model,
            temperature=temperature,
        )


research_agent = Agent(
    name="资料收集 Agent",
    role="围绕用户主题提取已有材料中的关键信息，并给出还需要补充检索的方向。",
    goal="帮助用户快速建立对一个主题的背景理解、信息缺口和后续资料收集路径。",
    output_format="""
请输出：
## 1. 主题背景
## 2. 已有材料中的关键信息
## 3. 信息缺口
## 4. 建议补充检索的问题
## 5. 可用关键词
""".strip(),
)

reading_agent = Agent(
    name="阅读理解 Agent",
    role="阅读和理解长文本、报告、网页摘录、会议记录或用户粘贴的资料。",
    goal="提取核心观点、重要事实、关键数据、争议点和可行动信息。",
    output_format="""
请输出：
## 1. 核心摘要
## 2. 关键观点
## 3. 重要事实或数据
## 4. 潜在问题或风险
## 5. 值得继续追问的点
""".strip(),
)

organize_agent = Agent(
    name="结构化整理 Agent",
    role="将杂乱信息整理成清晰的结构、表格、清单和知识卡片。",
    goal="把信息从不可直接使用的原始材料，转化为便于阅读、复用和执行的结构化内容。",
    output_format="""
请输出：
## 1. 信息总览
## 2. 分类整理
## 3. 重点清单
## 4. 待办事项
## 5. 可复用知识卡片
""".strip(),
)

planning_agent = Agent(
    name="任务规划 Agent",
    role="将复杂目标拆解为阶段、任务、优先级和执行步骤。",
    goal="帮助用户把一个模糊目标变成可以执行的计划。",
    output_format="""
请输出：
## 1. 目标澄清
## 2. 阶段拆解
## 3. 任务清单
## 4. 优先级排序
## 5. 时间安排建议
## 6. 风险与备选方案
""".strip(),
)

writing_agent = Agent(
    name="内容生成 Agent",
    role="根据前面 Agent 的结果生成最终可交付内容。",
    goal="输出邮件、方案、汇报稿、文章初稿、复盘报告或项目说明。",
    output_format="""
请输出：
## 1. 最终成稿
## 2. 可直接复制使用的版本
## 3. 可选标题
## 4. 后续优化建议
""".strip(),
)

AGENTS: Dict[str, Agent] = {
    "资料收集 Agent": research_agent,
    "阅读理解 Agent": reading_agent,
    "结构化整理 Agent": organize_agent,
    "任务规划 Agent": planning_agent,
    "内容生成 Agent": writing_agent,
}


def build_markdown_report(task: str, context: str, results: Dict[str, str]) -> str:
    """构建可导出的 Markdown 报告。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""# 通用型 AI 工作流助手运行报告

生成时间：{now}

## 用户任务

{task}

## 原始上下文

{context if context.strip() else "未提供额外上下文。"}

"""

    for agent_name, content in results.items():
        report += f"\n---\n\n# {agent_name}\n\n{content}\n"

    return report


st.set_page_config(
    page_title="通用型 AI 工作流助手",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 通用型 AI 工作流助手")
st.caption("多 Agent 协作：资料收集 · 阅读理解 · 结构化整理 · 任务规划 · 内容生成")

with st.sidebar:
    st.header("配置")

    model = st.text_input("模型名称", value=DEFAULT_MODEL)

    mode = st.radio(
        "运行模式",
        ["完整工作流", "单 Agent 模式"],
        index=0,
    )

    selected_agent = None
    if mode == "单 Agent 模式":
        selected_agent = st.selectbox("选择 Agent", list(AGENTS.keys()))

    st.divider()
    st.markdown("### 使用说明")
    st.markdown(
        """
1. 输入一个复杂目标。
2. 粘贴相关资料、会议记录或文档内容。
3. 运行完整工作流。
4. 下载 Markdown 报告。
        """
    )

    st.divider()
    st.markdown("### 适用场景")
    st.markdown(
        """
- 资料整理
- 项目规划
- 会议复盘
- 报告撰写
- 学习总结
- 内容创作
        """
    )

col1, col2 = st.columns([1, 1])

with col1:
    task = st.text_area(
        "请输入你的目标或任务",
        height=180,
        placeholder="例如：帮我围绕 AI 工作流助手设计一个产品方案，并生成可执行计划。",
    )

with col2:
    context = st.text_area(
        "请粘贴相关资料、文档、会议记录或背景信息",
        height=180,
        placeholder="可以为空；也可以粘贴长文本、报告、网页摘录、会议纪要等。",
    )

run_button = st.button("开始运行", type="primary", use_container_width=True)

if "last_results" not in st.session_state:
    st.session_state.last_results = None
if "last_report" not in st.session_state:
    st.session_state.last_report = None

if run_button:
    if not task.strip():
        st.warning("请先输入任务。")
    else:
        if mode == "完整工作流":
            st.subheader("完整工作流运行结果")
            results: Dict[str, str] = {}
            accumulated_context = context

            progress = st.progress(0)
            status = st.empty()

            workflow_order = list(AGENTS.keys())

            for idx, agent_name in enumerate(workflow_order):
                status.info(f"正在运行：{agent_name}")
                agent = AGENTS[agent_name]
                output = agent.run(task=task, context=accumulated_context, model=model)
                results[agent_name] = output
                accumulated_context += f"\n\n---\n\n{agent_name} 输出：\n{output}"
                progress.progress((idx + 1) / len(workflow_order))

            status.success("完整工作流已完成。")
            st.session_state.last_results = results
            st.session_state.last_report = build_markdown_report(task, context, results)

        else:
            st.subheader(f"{selected_agent} 运行结果")
            agent = AGENTS[selected_agent]
            output = agent.run(task=task, context=context, model=model)
            results = {selected_agent: output}
            st.session_state.last_results = results
            st.session_state.last_report = build_markdown_report(task, context, results)

if st.session_state.last_results:
    for agent_name, content in st.session_state.last_results.items():
        with st.expander(agent_name, expanded=True):
            st.markdown(content)

    st.download_button(
        label="下载 Markdown 报告",
        data=st.session_state.last_report,
        file_name="ai_workflow_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

st.divider()
st.subheader("示例任务")

example_1 = "我想设计一个个人知识管理系统，用于整理每天看到的文章、会议记录和想法，请帮我分析需求、拆解功能，并生成执行计划。"
example_2 = "请帮我把下面的会议纪要整理成项目计划，提取关键结论、待办事项、负责人和风险点。"
example_3 = "我想做一个 AI 辅助写作工作流，用于生成选题、整理素材、输出初稿和修改润色，请帮我设计完整方案。"

with st.expander("示例 1：个人知识管理"):
    st.code(example_1, language="text")

with st.expander("示例 2：会议纪要复盘"):
    st.code(example_2, language="text")

with st.expander("示例 3：AI 辅助写作"):
    st.code(example_3, language="text")
