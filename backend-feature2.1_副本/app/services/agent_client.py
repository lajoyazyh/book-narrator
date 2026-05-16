# app/services/agent_client.py

from __future__ import annotations

import os
from typing import Any

import requests


AGENT_BASE_URL = os.getenv("AGENT_BASE_URL", "http://localhost:8000")


def check_agent_health(timeout: int = 10) -> dict[str, Any]:
    """
    检查 Agent API 是否可用。
    """
    url = f"{AGENT_BASE_URL}/api/v1/health"

    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Agent health 检查失败：无法连接 Agent 服务，url={url}，error={str(e)}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Agent health 检查超时，url={url}"
        ) from e

    if response.status_code >= 400:
        raise RuntimeError(
            f"Agent health 检查失败：status={response.status_code}, "
            f"response={response.text}"
        )

    try:
        return response.json()
    except Exception:
        return {"message": response.text}


def run_agent(
        user_request: str,
        reset_context: bool = True,
        timeout: int = 1200,
) -> dict[str, Any]:
    """
    调用 Agent 核心运行接口。

    Agent API:
    POST /api/v1/agent/run

    body:
    {
      "user_request": "...",
      "reset_context": true
    }
    """
    url = f"{AGENT_BASE_URL}/api/v1/agent/run"

    payload = {
        "user_request": user_request,
        "reset_context": reset_context,
    }

    try:
        response = requests.post(url, json=payload, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(
            f"Agent 调用失败：无法连接 Agent 服务，url={url}，payload={payload}"
        ) from e
    except requests.exceptions.Timeout as e:
        raise RuntimeError(
            f"Agent 调用超时：url={url}，timeout={timeout}，payload={payload}"
        ) from e

    if response.status_code >= 400:
        raise RuntimeError(
            f"Agent 调用失败：status={response.status_code}, "
            f"response={response.text}, "
            f"payload={payload}"
        )

    try:
        return response.json()
    except Exception:
        return {
            "result": response.text,
            "raw_text": response.text,
        }