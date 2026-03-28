"""
多 Agent 软件开发框架 - 主 Crew 定义
基于 CrewAI 的层级流程，Manager Agent 作为总指挥协调所有开发 Agent。
每个 Agent 使用独立的模型和 API Key，共用同一个 BASE URL。
"""

import os
import httpx
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from yuri.tools.file_tools import write_file, read_file, list_directory


def _make_no_proxy_http_client() -> httpx.Client:
    """
    创建一个绕过系统代理、禁用 SSL 验证的 httpx 客户端。
    系统代理 127.0.0.1:9674 (Clash/V2Ray) 会导致 SSL EOF 错误，
    必须直连 timesniper.club。
    """
    transport = httpx.HTTPTransport(verify=False)
    return httpx.Client(
        mounts={"https://": transport, "http://": transport},
        timeout=120.0,
    )


def _make_llm(model: str, api_key_env: str) -> LLM:
    """
    创建一个 LLM 实例，使用共享的 BASE_URL 和指定的 API Key。
    """
    return LLM(
        model=f"openai/{model}",
        base_url=os.getenv("CUSTOM_BASE_URL", "https://timesniper.club/v1"),
        api_key=os.getenv(api_key_env, ""),
    )


@CrewBase
class SoftwareDevCrew:
    """多 Agent 软件开发框架 Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ─────────────────────────────────────────────
    # LLM 实例（每个 Agent 独立）
    # ─────────────────────────────────────────────

    @property
    def manager_llm(self) -> LLM:
        """Manager Agent LLM: gpt-5.4"""
        return _make_llm(
            model=os.getenv("MANAGER_MODEL", "gpt-5.4"),
            api_key_env="MANAGER_API_KEY",
        )

    @property
    def pm_llm(self) -> LLM:
        """PM Agent LLM: gpt-5.4"""
        return _make_llm(
            model=os.getenv("PM_MODEL", "gpt-5.4"),
            api_key_env="PM_API_KEY",
        )

    @property
    def claude_llm(self) -> LLM:
        """Frontend / Backend / Integration Agent LLM: claude-sonnet-4-6"""
        return _make_llm(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            api_key_env="CLAUDE_API_KEY",
        )

    @property
    def qa_llm(self) -> LLM:
        """QA Agent LLM: gpt-5.4"""
        return _make_llm(
            model=os.getenv("QA_MODEL", "gpt-5.4"),
            api_key_env="QA_API_KEY",
        )

    # ─────────────────────────────────────────────
    # Agent 定义
    # ─────────────────────────────────────────────

    def manager_agent(self) -> Agent:
        """总指挥 Agent：协调所有开发 Agent（gpt-5.4）
        注意：不加 @agent 装饰器，避免被加入 self.agents 列表，
        因为层级流程中 manager_agent 单独通过 Crew(manager_agent=...) 传入。
        """
        return Agent(
            config=self.agents_config["manager_agent"],
            llm=self.manager_llm,
            tools=[],
            allow_delegation=True,
            verbose=True,
        )

    @agent
    def pm_agent(self) -> Agent:
        """产品经理 Agent：分析需求，输出技术规格（gpt-5.4）"""
        return Agent(
            config=self.agents_config["pm_agent"],
            llm=self.pm_llm,
            tools=[write_file],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def frontend_agent(self) -> Agent:
        """前端工程师 Agent：生成前端代码（claude-sonnet-4-6）"""
        return Agent(
            config=self.agents_config["frontend_agent"],
            llm=self.claude_llm,
            tools=[write_file, read_file, list_directory],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def backend_agent(self) -> Agent:
        """后端工程师 Agent：生成后端代码（claude-sonnet-4-6）"""
        return Agent(
            config=self.agents_config["backend_agent"],
            llm=self.claude_llm,
            tools=[write_file, read_file, list_directory],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def integration_agent(self) -> Agent:
        """集成工程师 Agent：前后端接口联调（claude-sonnet-4-6）"""
        return Agent(
            config=self.agents_config["integration_agent"],
            llm=self.claude_llm,
            tools=[read_file, write_file, list_directory],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def qa_agent(self) -> Agent:
        """QA 工程师 Agent：需求验证与测试（gpt-5.4）"""
        return Agent(
            config=self.agents_config["qa_agent"],
            llm=self.qa_llm,
            tools=[read_file, write_file],
            allow_delegation=False,
            verbose=True,
        )

    # ─────────────────────────────────────────────
    # Task 定义
    # ─────────────────────────────────────────────

    @task
    def requirements_analysis_task(self) -> Task:
        """需求分析任务：将用户需求转化为技术规格文档"""
        return Task(
            config=self.tasks_config["requirements_analysis_task"],
            output_file="output/01_tech_spec.md",
        )

    @task
    def frontend_dev_task(self) -> Task:
        """前端开发任务：根据技术规格生成前端代码"""
        return Task(
            config=self.tasks_config["frontend_dev_task"],
            context=[self.requirements_analysis_task()],
            output_file="output/02_frontend_code.md",
        )

    @task
    def backend_dev_task(self) -> Task:
        """后端开发任务：根据技术规格生成后端代码"""
        return Task(
            config=self.tasks_config["backend_dev_task"],
            context=[self.requirements_analysis_task()],
            output_file="output/03_backend_code.md",
        )

    @task
    def integration_task(self) -> Task:
        """集成联调任务：确保前后端接口对齐"""
        return Task(
            config=self.tasks_config["integration_task"],
            context=[self.frontend_dev_task(), self.backend_dev_task()],
            output_file="output/04_integration_report.md",
        )

    @task
    def qa_validation_task(self) -> Task:
        """需求验证任务：对照原始需求验证最终实现"""
        return Task(
            config=self.tasks_config["qa_validation_task"],
            context=[self.integration_task()],
            output_file="output/05_qa_report.md",
        )

    # ─────────────────────────────────────────────
    # Crew 定义
    # ─────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        """
        创建多 Agent 软件开发 Crew。
        使用层级流程（Hierarchical），Manager Agent 作为总指挥。
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.manager_agent(),
            verbose=True,
            planning=False,                   # 关闭 planning（避免 planning agent 超时）
            memory=False,                     # 关闭记忆（避免需要额外向量数据库）
            output_log_file="output/crew_execution.log",
        )
