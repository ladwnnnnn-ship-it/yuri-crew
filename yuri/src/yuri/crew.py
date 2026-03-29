"""
Multi-Agent Software Development Framework - Main Crew Definition
Based on CrewAI hierarchical process, Manager Agent coordinates all development Agents.
Each Agent uses an independent model and API Key, sharing the same BASE URL.
"""

import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from yuri.tools.file_tools import write_file, read_file, list_directory

# ---------------------------------------------------------------------------
# Default API keys / config (used when env vars are not set, e.g. on cloud)
# ---------------------------------------------------------------------------
_DEFAULT_GPT_BASE_URL = "https://timesniper.club/v1"
_DEFAULT_CLAUDE_BASE_URL = "https://flash.timesniper.club/v1"
_DEFAULT_MANAGER_KEY = "sk-XsEi3ZgLNM2qwcLLRu1iay089NmBnjXyDTQGkWhsmxYFel0I"
_DEFAULT_PM_KEY = "sk-d7tpsFfQgSQ02L89eP9OzgKMpxjcF7OKV07GgkgnkQcz4LVc"
_DEFAULT_CLAUDE_KEY = "sk-iuKk2dAVf40Pe34I9IoUaVpJPqBmHyulB2iVFucvyMzlJUrd"
_DEFAULT_FRONTEND_KEY = "sk-iuKk2dAVf40Pe34I9IoUaVpJPqBmHyulB2iVFucvyMzlJUrd"
_DEFAULT_BACKEND_KEY = "sk-iuKk2dAVf40Pe34I9IoUaVpJPqBmHyulB2iVFucvyMzlJUrd"
_DEFAULT_INTEGRATION_KEY = "sk-iuKk2dAVf40Pe34I9IoUaVpJPqBmHyulB2iVFucvyMzlJUrd"

# Set OPENAI_API_KEY so crewai v1.x native provider initializes without error.
_primary_key = (
    os.getenv("MANAGER_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or _DEFAULT_MANAGER_KEY
)
os.environ.setdefault("OPENAI_API_KEY", _primary_key)


def _make_llm(model: str, api_key: str, use_claude: bool = False) -> LLM:
    """
    Create an LLM instance using the appropriate BASE_URL based on model type.
    - CLAUDE models → https://flash.timesniper.club/v1  (openai-compatible)
    - GPT models    → https://timesniper.club/v1         (openai-compatible)
    Both use 'openai/' prefix so litellm routes via OpenAI-compatible endpoint.
    """
    if use_claude:
        base_url = os.getenv("CLAUDE_BASE_URL", _DEFAULT_CLAUDE_BASE_URL)
    else:
        base_url = os.getenv("GPT_BASE_URL", _DEFAULT_GPT_BASE_URL)
    model_name = model
    return LLM(
        model=model_name,
        base_url=base_url,
        api_key=api_key,
        stream=False,
    )


@CrewBase
class SoftwareDevCrew:
    """Multi-Agent Software Development Framework Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ─────────────────────────────────────────────
    # LLM instances (one per Agent role)
    # ─────────────────────────────────────────────

    @property
    def manager_llm(self) -> LLM:
        """Manager Agent LLM: gpt-5.4 (GPT)"""
        return _make_llm(
            model=os.getenv("MANAGER_MODEL", "gpt-5.4"),
            api_key=os.getenv("MANAGER_API_KEY", _primary_key),
            use_claude=False,
        )

    @property
    def pm_llm(self) -> LLM:
        """PM Agent LLM: gpt-5.4 (GPT)"""
        return _make_llm(
            model=os.getenv("PM_MODEL", "gpt-5.4"),
            api_key=os.getenv("PM_API_KEY", _primary_key),
            use_claude=False,
        )

    @property
    def claude_llm(self) -> LLM:
        """Frontend / Backend / Integration Agent LLM: claude-sonnet-4-5 (Claude)"""
        return _make_llm(
            model=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("CLAUDE_API_KEY", _DEFAULT_CLAUDE_KEY),
            use_claude=True,
        )

    @property
    def frontend_llm(self) -> LLM:
        """Frontend Agent LLM"""
        return _make_llm(
            model=os.getenv("FRONTEND_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("FRONTEND_API_KEY", _DEFAULT_FRONTEND_KEY),
            use_claude=True,
        )

    @property
    def backend_llm(self) -> LLM:
        """Backend Agent LLM"""
        return _make_llm(
            model=os.getenv("BACKEND_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("BACKEND_API_KEY", _DEFAULT_BACKEND_KEY),
            use_claude=True,
        )

    @property
    def integration_llm(self) -> LLM:
        """Integration Agent LLM"""
        return _make_llm(
            model=os.getenv("INTEGRATION_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("INTEGRATION_API_KEY", _DEFAULT_INTEGRATION_KEY),
            use_claude=True,
        )

    @property
    def qa_llm(self) -> LLM:
        """QA Agent LLM: gpt-5.4 (GPT)"""
        return _make_llm(
            model=os.getenv("QA_MODEL", "gpt-5.4"),
            api_key=os.getenv("QA_API_KEY", _primary_key),
            use_claude=False,
        )

    # ─────────────────────────────────────────────
    # Agent definitions
    # ─────────────────────────────────────────────

    def manager_agent(self) -> Agent:
        """Manager Agent: coordinates all development Agents.
        No @agent decorator - passed separately via Crew(manager_agent=...).
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
        """Product Manager Agent: analyzes requirements, outputs tech spec."""
        return Agent(
            config=self.agents_config["pm_agent"],
            llm=self.pm_llm,
            tools=[write_file],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def frontend_agent(self) -> Agent:
        """Frontend Engineer Agent: generates frontend code."""
        return Agent(
            config=self.agents_config["frontend_agent"],
            llm=self.frontend_llm,
            tools=[write_file, read_file, list_directory],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def backend_agent(self) -> Agent:
        """Backend Engineer Agent: generates backend code."""
        return Agent(
            config=self.agents_config["backend_agent"],
            llm=self.backend_llm,
            tools=[write_file, read_file, list_directory],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def integration_agent(self) -> Agent:
        """Integration Engineer Agent: aligns frontend/backend interfaces."""
        return Agent(
            config=self.agents_config["integration_agent"],
            llm=self.integration_llm,
            tools=[read_file, write_file, list_directory],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def qa_agent(self) -> Agent:
        """QA Engineer Agent: validates requirements and tests."""
        return Agent(
            config=self.agents_config["qa_agent"],
            llm=self.qa_llm,
            tools=[read_file, write_file],
            allow_delegation=False,
            verbose=True,
        )

    # ─────────────────────────────────────────────
    # Task definitions
    # ─────────────────────────────────────────────

    @task
    def requirements_analysis_task(self) -> Task:
        """Requirements analysis: convert user needs into tech spec document."""
        return Task(
            config=self.tasks_config["requirements_analysis_task"],
        )

    @task
    def frontend_dev_task(self) -> Task:
        """Frontend development: generate frontend code from tech spec."""
        return Task(
            config=self.tasks_config["frontend_dev_task"],
            context=[self.requirements_analysis_task()],
        )

    @task
    def backend_dev_task(self) -> Task:
        """Backend development: generate backend code from tech spec."""
        return Task(
            config=self.tasks_config["backend_dev_task"],
            context=[self.requirements_analysis_task()],
        )

    @task
    def integration_task(self) -> Task:
        """Integration: ensure frontend/backend interface alignment."""
        return Task(
            config=self.tasks_config["integration_task"],
            context=[self.frontend_dev_task(), self.backend_dev_task()],
        )

    @task
    def qa_validation_task(self) -> Task:
        """QA validation: verify final implementation against original requirements."""
        return Task(
            config=self.tasks_config["qa_validation_task"],
            context=[self.integration_task()],
        )

    # ─────────────────────────────────────────────
    # Crew definition
    # ─────────────────────────────────────────────

    @crew
    def crew(self) -> Crew:
        """
        Create the Multi-Agent Software Development Crew.
        Uses hierarchical process with Manager Agent as coordinator.
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.manager_agent(),
            verbose=True,
            planning=False,
            memory=False,
        )
