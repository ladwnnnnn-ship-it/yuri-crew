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
    transport = httpx.HTTPTransport(verify=False)
    client = httpx.Client(
        mounts={'https://': transport, 'http://': transport},
        limits=httpx.Limits(max_connections=1000, max_keepalive_connections=100),
        follow_redirects=True,
        timeout=120.0,
    )
    print(f'[DEBUG #{call_count[0]}] 创建无代理客户端 id={id(client)}')
    return client

_oai_llm.OpenAIChatCompletion._get_sync_http_client = staticmethod(_patched_get_sync_http_client)
litellm.client_session = _patched_get_sync_http_client()
litellm.in_memory_llm_clients_cache.flush_cache()
print(f'[SETUP] client_session id={id(litellm.client_session)}')

# 拦截 _get_openai_client 看它用了哪个 http_client
orig_get_client = _oai_llm.OpenAIChatCompletion._get_openai_client
def debug_get_client(self, is_async, api_key=None, api_base=None, **kwargs):
    result = orig_get_client(self, is_async=is_async, api_key=api_key, api_base=api_base, **kwargs)
    if result and hasattr(result, '_client'):
        print(f'[DEBUG] OpenAI client._client id={id(result._client)}, type={type(result._client)}')
        if hasattr(result._client, '_transport'):
            print(f'[DEBUG] transport={result._client._transport}')
        if hasattr(result._client, '_mounts'):
            print(f'[DEBUG] mounts={result._client._mounts}')
    return result
_oai_llm.OpenAIChatCompletion._get_openai_client = debug_get_client

# 测试1: 直接 litellm.completion
print('\n=== 测试1: litellm.completion ===')
resp = litellm.completion(
    model='openai/gpt-5.4',
    messages=[{'role': 'user', 'content': '一个字'}],
    api_base='https://timesniper.club/v1',
    api_key=os.getenv('MANAGER_API_KEY'),
    max_tokens=5,
)
print('成功:', resp.choices[0].message.content)

# 测试2: crewAI LLM.call
print('\n=== 测试2: crewAI LLM.call ===')
litellm.in_memory_llm_clients_cache.flush_cache()
from crewai import LLM
llm = LLM(
    model='openai/gpt-5.4',
    base_url='https://timesniper.club/v1',
    api_key=os.getenv('MANAGER_API_KEY'),
)
r = llm.call([{'role': 'user', 'content': '一个字'}])
print('crewAI LLM 成功:', r)
