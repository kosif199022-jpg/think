"""
OpenAI & ChatGPT Compatible Bridge for KOSIF Think.
Allows any ChatGPT client, Custom GPT, Cursor, Continue.dev, or external tool
to communicate with KOSIF Think using standard OpenAI /v1/chat/completions endpoints.
"""

import json
import time
import uuid
from typing import Dict, Any, List, Optional
from ..core.executor import ThinkExecutor, ExecutionResult

class OpenAIBridge:
    """Translates standard OpenAI chat completions requests into KOSIF Think pipeline execution."""

    def __init__(self, executor: ThinkExecutor):
        self.executor = executor

    def list_models(self) -> Dict[str, Any]:
        """Returns OpenAI-compatible /v1/models response."""
        now = int(time.time())
        return {
            "object": "list",
            "data": [
                {
                    "id": "kosif-think-v1",
                    "object": "model",
                    "created": now,
                    "owned_by": "kosif",
                    "permission": [],
                    "root": "kosif-think-v1",
                    "parent": None
                },
                {
                    "id": "kosif-think-reasoning",
                    "object": "model",
                    "created": now,
                    "owned_by": "kosif",
                    "permission": [],
                    "root": "kosif-think-reasoning",
                    "parent": None
                },
                {
                    "id": "kosif-think-coder",
                    "object": "model",
                    "created": now,
                    "owned_by": "kosif",
                    "permission": [],
                    "root": "kosif-think-coder",
                    "parent": None
                }
            ]
        }

    async def handle_chat_completion(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processes an incoming OpenAI-style chat completion payload."""
        t0 = time.perf_counter()
        messages = request_data.get("messages", [])
        model = request_data.get("model", "kosif-think-v1")
        temperature = float(request_data.get("temperature", 0.7))

        # Extract last user message
        user_prompt = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_prompt = m.get("content", "")
                break

        if not user_prompt:
            user_prompt = "Hello"

        # Execute via ThinkExecutor
        result: ExecutionResult = await self.executor.execute_goal(raw_prompt=user_prompt)

        # Format output message
        if result.status == "human_checkpoint":
            reply_content = (
                f"🛡️ [KOSIF Think Checkpoint]\n"
                f"{result.checkpoint_details.get('message', 'Human verification required.')}\n"
                f"Task ID: {result.task_id}"
            )
        elif result.status == "completed":
            reply_content = (
                f"🧠 [KOSIF Think Completed in {result.duration_ms}ms]\n\n"
                f"{json.dumps(result.output, ensure_ascii=False, indent=2) if result.output else 'Goal successfully executed.'}"
            )
        else:
            reply_content = f"❌ [KOSIF Think Status: {result.status}]\nError: {result.error}"

        call_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
        prompt_tokens = len(user_prompt.split()) * 2
        completion_tokens = len(reply_content.split()) * 2

        response = {
            "id": call_id,
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            "kosif_metadata": {
                "task_id": result.task_id,
                "status": result.status,
                "duration_ms": result.duration_ms,
                "steps_executed": result.steps_executed
            }
        }
        return response
