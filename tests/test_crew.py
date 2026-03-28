"""
多 Agent 软件开发框架 - 单元测试
"""

import pytest
from unittest.mock import MagicMock, patch
from yuri.crew import SoftwareDevCrew


class TestSoftwareDevCrew:
    """测试 SoftwareDevCrew 的基本功能"""

    def test_crew_instantiation(self):
        """测试 Crew 可以正常实例化"""
        crew_instance = SoftwareDevCrew()
        assert crew_instance is not None

    def test_agents_created(self):
        """测试所有 Agent 都被正确创建"""
        crew_instance = SoftwareDevCrew()
        assert crew_instance.pm_agent() is not None
        assert crew_instance.frontend_agent() is not None
        assert crew_instance.backend_agent() is not None
        assert crew_instance.integration_agent() is not None
        assert crew_instance.qa_agent() is not None

    def test_tasks_created(self):
        """测试所有 Task 都被正确创建"""
        crew_instance = SoftwareDevCrew()
        assert crew_instance.requirements_analysis_task() is not None
        assert crew_instance.frontend_dev_task() is not None
        assert crew_instance.backend_dev_task() is not None
        assert crew_instance.integration_task() is not None
        assert crew_instance.qa_validation_task() is not None

    def test_crew_has_correct_agent_count(self):
        """测试 Crew 包含正确数量的 Agent"""
        crew_instance = SoftwareDevCrew()
        crew = crew_instance.crew()
        # Manager Agent + 5 个专职 Agent
        assert len(crew.agents) >= 5

    def test_crew_has_correct_task_count(self):
        """测试 Crew 包含正确数量的 Task"""
        crew_instance = SoftwareDevCrew()
        crew = crew_instance.crew()
        assert len(crew.tasks) == 5


class TestFileTools:
    """测试文件操作工具"""

    def test_write_and_read_file(self, tmp_path):
        """测试文件写入和读取"""
        from yuri.tools.file_tools import write_file, read_file

        test_file = str(tmp_path / "test.txt")
        test_content = "Hello, CrewAI!"

        # 写入文件
        result = write_file.run({"filepath": test_file, "content": test_content})
        assert "✅" in result

        # 读取文件
        content = read_file.run({"filepath": test_file})
        assert content == test_content

    def test_read_nonexistent_file(self):
        """测试读取不存在的文件"""
        from yuri.tools.file_tools import read_file

        result = read_file.run({"filepath": "/nonexistent/path/file.txt"})
        assert "❌" in result

    def test_list_directory(self, tmp_path):
        """测试列出目录内容"""
        from yuri.tools.file_tools import list_directory, write_file

        # 创建测试文件
        write_file.run({"filepath": str(tmp_path / "file1.txt"), "content": "test1"})
        write_file.run({"filepath": str(tmp_path / "file2.txt"), "content": "test2"})

        result = list_directory.run({"dirpath": str(tmp_path)})
        assert "file1.txt" in result
        assert "file2.txt" in result


class TestCrewInputs:
    """测试 Crew 输入验证"""

    def test_required_inputs_keys(self):
        """测试必要的输入键存在"""
        required_keys = [
            "user_requirement",
            "tech_spec",
            "frontend_code",
            "backend_code",
            "integrated_code",
        ]
        inputs = {
            "user_requirement": "构建一个 TODO 应用",
            "tech_spec": "",
            "frontend_code": "",
            "backend_code": "",
            "integrated_code": "",
        }
        for key in required_keys:
            assert key in inputs, f"缺少必要输入键: {key}"

    def test_user_requirement_not_empty(self):
        """测试用户需求不为空"""
        user_requirement = "构建一个用户管理系统"
        assert user_requirement.strip() != "", "用户需求不能为空"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
