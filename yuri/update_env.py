"""
Use CrewAI's internal PlusAPI to update crew environment variables.
"""
import sys
sys.path.insert(0, r"c:\Users\HUAWEI\Desktop\crewAI-main\.venv\Lib\site-packages")

import httpx

API_KEY = "pat_tRSRObestRClis-Q6sXP-AQWKqT1Ja7zjY7cjdTUu2k"
BASE_URL = "https://app.crewai.com"
CREW_UUID = "0a54e9ea-6b0b-4a10-a484-228081c29fcf"

ENV_VARS = {
    "OPENAI_API_KEY": "sk-XsEi3ZgLNM2qwcLLRu1iay089NmBnjXyDTQGkWhsmxYFel0I",
    "CUSTOM_BASE_URL": "https://timesniper.club/v1",
    "MANAGER_API_KEY": "sk-XsEi3ZgLNM2qwcLLRu1iay089NmBnjXyDTQGkWhsmxYFel0I",
    "MANAGER_MODEL": "gpt-5.4",
    "PM_API_KEY": "sk-d7tpsFfQgSQ02L89eP9OzgKMpxjcF7OKV07GgkgnkQcz4LVc",
    "PM_MODEL": "gpt-5.4",
    "CLAUDE_API_KEY": "sk-iuKk2dAVf40Pe34I9IoUaVpJPqBmHyulB2iVFucvyMzlJUrd",
    "CLAUDE_MODEL": "gpt-5.4",
    "QA_API_KEY": "sk-XsEi3ZgLNM2qwcLLRu1iay089NmBnjXyDTQGkWhsmxYFel0I",
    "QA_MODEL": "gpt-5.4",
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "CrewAI-CLI/1.12.2",
    "X-Crewai-Version": "1.12.2",
}

# Try different endpoints
endpoints_to_try = [
    ("PATCH", f"/crewai_plus/api/v1/crews/{CREW_UUID}"),
    ("PUT", f"/crewai_plus/api/v1/crews/{CREW_UUID}"),
    ("POST", f"/crewai_plus/api/v1/crews/{CREW_UUID}/env"),
    ("PUT", f"/crewai_plus/api/v1/crews/{CREW_UUID}/env"),
    ("PATCH", f"/crewai_plus/api/v1/crews/{CREW_UUID}/env"),
    ("POST", f"/crewai_plus/api/v1/crews/{CREW_UUID}/environment"),
    ("PUT", f"/crewai_plus/api/v1/crews/{CREW_UUID}/environment"),
]

payloads_to_try = [
    {"env": ENV_VARS},
    {"deploy": {"env": ENV_VARS}},
    {"environment_variables": ENV_VARS},
    ENV_VARS,
]

with httpx.Client(verify=True, timeout=30) as client:
    for method, endpoint in endpoints_to_try:
        for payload in payloads_to_try[:1]:  # try first payload format
            url = f"{BASE_URL}{endpoint}"
            print(f"Trying {method} {url}...")
            try:
                resp = client.request(method, url, headers=headers, json=payload)
                print(f"  Status: {resp.status_code}")
                if resp.status_code not in (404, 405):
                    print(f"  Response: {resp.text[:500]}")
                    break
            except Exception as e:
                print(f"  Error: {e}")
