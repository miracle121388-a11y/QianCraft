from __future__ import annotations

import base64
import hashlib
import io
import mimetypes
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
            "supports_image_to_image": (
                configured and self.settings.image_provider == "dashscope-native"
            ),
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
        reference_image_path: Path | None = None,
    ) -> dict[str, Any]:
        status = self.status()
        if not status["configured"]:
            raise ValueError(status["detail"])
        if not prompt.strip():
            raise ValueError("图像生成提示词不能为空。")

        dashscope_native = self.settings.image_provider == "dashscope-native"
        reference_sha256 = ""
        reference_content: dict[str, str] | None = None
        if reference_image_path is not None:
            reference_path = reference_image_path.resolve()
            if not reference_path.is_file():
                raise FileNotFoundError(f"图生图参考图片不存在：{reference_path}")
            if not dashscope_native:
                raise ValueError("当前图像 provider 不支持本适配器的图生图输入。")
            reference_bytes = reference_path.read_bytes()
            if len(reference_bytes) > 10 * 1024 * 1024:
                raise RuntimeError("图生图参考图片超过 10MB 安全上限。")
            with Image.open(io.BytesIO(reference_bytes)) as reference_image:
                reference_image.verify()
            media_type = mimetypes.guess_type(reference_path.name)[0] or "image/png"
            reference_sha256 = hashlib.sha256(reference_bytes).hexdigest()
            reference_content = {
                "image": (
                    f"data:{media_type};base64,"
                    + base64.b64encode(reference_bytes).decode("ascii")
                )
            }
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
            content = []
            if reference_content is not None:
                content.append(reference_content)
            content.append({"text": prompt.strip()})
            payload = {
                "model": self.settings.image_model,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": content,
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
            width, height = image.size
            image_format = str(image.format or "").upper()
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
            "width": width,
            "height": height,
            "format": image_format,
            "mode": "image_to_image" if reference_image_path is not None else "text_to_image",
            "prompt_sha256": hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest(),
            "reference_sha256": reference_sha256,
        }


def image_provider_status(settings: Settings | None = None) -> dict[str, Any]:
    return ImageGenerationAdapter(settings).status()
