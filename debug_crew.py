import os, sys, warnings
sys.path.insert(0, 'src')
from dotenv import load_dotenv
load_dotenv('c:/Users/HUAWEI/Desktop/crewAI-main/.env')
import httpx
warnings.filterwarnings('ignore')
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

import litellm
import litellm.llms.openai.openai as _oai_llm

call_count = [0]

def _patched_get_sync_http_client():
    call_count[0] += 1
    import traceback
    print(f'\n[DEBUG #{call_count[0]}] _get_sync_http_client called from:')
    traceback.print_stack(limit=6)
    transport = httpx.HTTPTransport(verify=False)
    client = httpx.Client(
        mounts={'https://': transport, 'http://': transport},
        limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100),
        follow_redirects=True,
        timeout=120.0,
    )
    return client

_oai_llm.OpenAIChatCompletion._get_sync_http_client = staticmethod(_patched_get_sync_http_client)
litellm.client_session = _patched_get_sync_http_client()
litellm.in_memory_llm_clients_cache.flush_cache()

print('[PATCH] Done. Now running crew...\n')

from yuri.crew import SoftwareDevCrew

inputs = {
    'user_requirement': '构建一个简单的待办事项（TODO）管理应用',
    'tech_spec': '',
    'frontend_code': '',
    'backend_code': '',
    'integrated_code': '',
}

try:
    result = SoftwareDevCrew().crew().kickoff(inputs=inputs)
    print('SUCCESS:', result)
except Exception as e:
    print(f'\n[FAILED] {type(e).__name__}: {e}')
    print(f'_get_sync_http_client 被调用了 {call_count[0]} 次')
