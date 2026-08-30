from __future__ import annotations

import base64
import hashlib
import io
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
from PIL import Image

from app.config import Settings, load_settings


class ImageGenerationAdapter:
    """Small boundary for OpenAI-compatible and DashScope image APIs."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or load_settings()

    def status(self) -> dict[str, Any]:
        configured = self.settings.has_image_provider
        return {
            "provider": self.settings.image_provider or "unconfigured",
            "model": self.settings.image_model or "",
            "base_url_configured": bool(self.settings.image_base_url),
            "credential_configured": bool(self.settings.image_api_key),
            "configured": configured,
            "detail": (
                "图像生成适配器已就绪。"
                if configured
                else "未配置 IMAGE_PROVIDER / IMAGE_API_KEY / IMAGE_BASE_URL / IMAGE_MODEL。"
            ),
        }

    def generate(
        self,
        prompt: str,
        output_path: Path,
        *,
        size: str = "1024x1024",
    ) -> dict[str, Any]:
        status = self.status()
        if not status["configured"]:
            raise ValueError(status["detail"])
        if not prompt.strip():
            raise ValueError("图像生成提示词不能为空。")

        dashscope_native = self.settings.image_provider == "dashscope-native"
        endpoint = (
            f"{self.settings.image_base_url}/services/aigc/multimodal-generation/generation"
            if dashscope_native
            else f"{self.settings.image_base_url}/images/generations"
        )
        headers = {
            "Authorization": f"Bearer {self.settings.image_api_key}",
            "Content-Type": "application/json",
        }
        if dashscope_native:
            payload = {
                "model": self.settings.image_model,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": prompt.strip()}],
                        }
                    ]
                },
                "parameters": {
                    "n": 1,
                    "prompt_extend": True,
                    "size": size.replace("x", "*").replace("X", "*"),
                    "watermark": False,
                },
            }
        else:
            payload = {
                "model": self.settings.image_model,
                "prompt": prompt.strip(),
                "size": size,
                "n": 1,
                "response_format": "b64_json",
            }
        with httpx.Client(
            timeout=self.settings.image_timeout_seconds,
            follow_redirects=True,
        ) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            body = response.json()
            if dashscope_native:
                try:
                    asset_url = body["output"]["choices"][0]["message"]["content"][0][
                        "image"
                    ]
                except (KeyError, IndexError, TypeError) as exc:
                    raise RuntimeError("千问图像服务没有返回可读取的图片地址。") from exc
                asset_response = client.get(str(asset_url))
                asset_response.raise_for_status()
                image_bytes = asset_response.content
            else:
                items = body.get("data", []) if isinstance(body, dict) else []
                if not items or not isinstance(items[0], dict):
                    raise RuntimeError("图像服务没有返回可读取的 data[0]。")
                item = items[0]
                if item.get("b64_json"):
                    image_bytes = base64.b64decode(str(item["b64_json"]), validate=True)
                elif item.get("url"):
                    asset_response = client.get(str(item["url"]))
                    asset_response.raise_for_status()
                    image_bytes = asset_response.content
                else:
                    raise RuntimeError("图像服务返回中缺少 b64_json 或 url。")

        if len(image_bytes) > 25 * 1024 * 1024:
            raise RuntimeError("图像服务返回文件超过 25MB 安全上限。")
        with Image.open(io.BytesIO(image_bytes)) as image:
            image.verify()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = output_path.with_name(f".{output_path.name}.{os.getpid()}.tmp")
        temporary.write_bytes(image_bytes)
        temporary.replace(output_path)
        return {
            "provider": self.settings.image_provider,
            "model": self.settings.image_model,
            "generated_at": datetime.now(UTC).isoformat(),
            "path": str(output_path.resolve()),
            "sha256": hashlib.sha256(image_bytes).hexdigest(),
            "size": size,
        }


def image_provider_status(settings: Settings | None = None) -> dict[str, Any]:
    return ImageGenerationAdapter(settings).status()
