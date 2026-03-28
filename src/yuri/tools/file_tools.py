"""
文件操作工具集
供各 Agent 读写生成的代码文件
"""

import os
from crewai.tools import tool


@tool("write_file")
def write_file(filepath: str, content: str) -> str:
    """
    将内容写入指定文件路径。
    参数：
        filepath: 文件路径（相对或绝对路径）
        content: 要写入的文件内容
    返回：成功或失败信息
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ 文件已成功写入: {filepath}"
    except Exception as e:
        return f"❌ 写入文件失败: {e}"


@tool("read_file")
def read_file(filepath: str) -> str:
    """
    读取指定文件路径的内容。
    参数：
        filepath: 文件路径（相对或绝对路径）
    返回：文件内容或错误信息
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"❌ 文件不存在: {filepath}"
    except Exception as e:
        return f"❌ 读取文件失败: {e}"


@tool("list_directory")
def list_directory(dirpath: str) -> str:
    """
    列出指定目录下的所有文件。
    参数：
        dirpath: 目录路径
    返回：文件列表
    """
    try:
        files = []
        for root, dirs, filenames in os.walk(dirpath):
            for filename in filenames:
                rel_path = os.path.relpath(os.path.join(root, filename), dirpath)
                files.append(rel_path)
        return "\n".join(files) if files else "目录为空"
    except Exception as e:
        return f"❌ 列出目录失败: {e}"
