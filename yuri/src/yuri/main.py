"""
多 Agent 软件开发框架 - 入口文件
使用方法：
    python -m yuri.main
    或
    crewai run (在 yuri/ 目录下)
"""

import os
import sys
import ssl
import warnings

from dotenv import load_dotenv

# 加载环境变量（含 CrewAI Token、OpenAI Key 等）
load_dotenv()

# ─── 代理/SSL 修复 ───────────────────────────────────────────────────────────
# 诊断结论：
#   系统代理 127.0.0.1:9674 (Clash/V2Ray) 无法转发 timesniper.club 的 HTTPS 请求。
#   直连（绕过代理）正常工作。
#
# 修复方案：对 openai SDK 内部的 SyncHttpxClientWrapper 打猴子补丁，
#   强制使用 无代理 + 禁用SSL验证 的 httpx transport。
# ────────────────────────────────────────────────────────────────────────────

import httpx

# 屏蔽 SSL 警告
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except Exception:
    pass

# 清空环境变量代理
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""

# ── 核心修复：补丁 litellm 的 _get_sync_http_client ─────────────────────────
# 经诊断：
#   - 系统代理 127.0.0.1:9674 无法转发 timesniper.club 的请求
#   - 直连时需要禁用 SSL 验证（verify=False）
#   - litellm 通过 _get_sync_http_client() 创建 httpx 客户端，需直接替换此方法
try:
    import litellm as _litellm
    import litellm.llms.openai.openai as _oai_llm

    def _patched_get_sync_http_client():
        """返回无代理、禁用 SSL 的 httpx 客户端"""
        transport = httpx.HTTPTransport(verify=False)
        return httpx.Client(
            mounts={"https://": transport, "http://": transport},
            limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100),
            follow_redirects=True,
            timeout=120.0,
        )

    # 替换静态方法
    _oai_llm.OpenAIChatCompletion._get_sync_http_client = staticmethod(
        _patched_get_sync_http_client
    )

    # 同时设置 client_session 作为双重保险
    _litellm.client_session = _patched_get_sync_http_client()

    # 清除 litellm 缓存的旧客户端（关键！避免用旧的代理客户端）
    try:
        _oai_llm.OpenAIChatCompletion._cache = {}
    except Exception:
        pass
    try:
        # litellm 使用 in_memory_llm_clients_cache 缓存 OpenAI 客户端
        _litellm.in_memory_llm_clients_cache.flush_cache()
    except Exception:
        pass
    try:
        _litellm.cache = None
    except Exception:
        pass

    print("[代理修复] ✅ 已补丁 litellm._get_sync_http_client（无代理+禁用SSL）")
except Exception as _patch_err:
    print(f"[代理修复] ⚠️ 补丁失败: {_patch_err}")
# ────────────────────────────────────────────────────────────────────────────

from yuri.crew import SoftwareDevCrew


def run():
    """
    启动多 Agent 软件开发框架。
    从命令行参数或交互式输入获取用户需求。
    """
    print("=" * 60)
    print("🚀 多 Agent 软件开发框架")
    print("=" * 60)

    # 获取用户需求
    if len(sys.argv) > 1:
        user_requirement = " ".join(sys.argv[1:])
    else:
        print("\n请输入您的产品需求（支持多行，输入完成后按 Ctrl+D 或 Ctrl+Z 结束）：\n")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        user_requirement = "\n".join(lines)

    if not user_requirement.strip():
        print("❌ 错误：需求不能为空！")
        sys.exit(1)

    print(f"\n📋 已接收需求：\n{user_requirement}\n")
    print("=" * 60)
    print("⚙️  正在启动 Agent 团队...")
    print("=" * 60)

    # 创建输出目录
    os.makedirs("output", exist_ok=True)

    # 启动 Crew
    inputs = {
        "user_requirement": user_requirement,
        "tech_spec": "",        # 由 requirements_analysis_task 填充
        "frontend_code": "",    # 由 frontend_dev_task 填充
        "backend_code": "",     # 由 backend_dev_task 填充
        "integrated_code": "",  # 由 integration_task 填充
    }

    result = SoftwareDevCrew().crew().kickoff(inputs=inputs)

    print("\n" + "=" * 60)
    print("✅ 开发框架执行完成！")
    print("=" * 60)
    print("\n📁 输出文件：")
    print("  - output/01_tech_spec.md        → 技术规格文档")
    print("  - output/02_frontend_code.md    → 前端代码")
    print("  - output/03_backend_code.md     → 后端代码")
    print("  - output/04_integration_report.md → 联调报告")
    print("  - output/05_qa_report.md        → QA 验证报告")
    print("  - output/crew_execution.log     → 执行日志")
    print("\n🔍 可在 https://app.crewai.com 查看详细追踪数据")
    print("\n最终结果摘要：")
    print(result)

    return result


def train():
    """训练 Crew（用于优化 Agent 行为）"""
    n_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    filename = sys.argv[3] if len(sys.argv) > 3 else "training_data.pkl"
    inputs = {
        "user_requirement": "构建一个简单的待办事项管理应用，支持增删改查",
        "tech_spec": "",
        "frontend_code": "",
        "backend_code": "",
        "integrated_code": "",
    }
    SoftwareDevCrew().crew().train(
        n_iterations=n_iterations,
        filename=filename,
        inputs=inputs,
    )


def replay():
    """重放指定任务"""
    task_id = sys.argv[2] if len(sys.argv) > 2 else None
    if not task_id:
        print("❌ 请提供 task_id：python -m yuri.main replay <task_id>")
        sys.exit(1)
    SoftwareDevCrew().crew().replay(task_id=task_id)


def test():
    """测试 Crew 执行"""
    n_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    openai_model = sys.argv[3] if len(sys.argv) > 3 else "gpt-4o"
    inputs = {
        "user_requirement": "构建一个简单的用户登录注册系统",
        "tech_spec": "",
        "frontend_code": "",
        "backend_code": "",
        "integrated_code": "",
    }
    SoftwareDevCrew().crew().test(
        n_iterations=n_iterations,
        openai_model_name=openai_model,
        inputs=inputs,
    )


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "run"
    if command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        run()
