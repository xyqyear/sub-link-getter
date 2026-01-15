import base64
import json

import requests

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def recognize_captcha(image_bytes: bytes, api_key: str) -> str | None:
    """
    Recognize captcha text using OpenRouter API with Gemini model.

    Args:
        image_bytes: Raw bytes of the captcha image
        api_key: OpenRouter API key

    Returns:
        Recognized captcha text or None if failed
    """
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{base64_image}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "google/gemini-3-flash-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This is a captcha image. Please recognize the text/characters shown in the image. Output ONLY the captcha text, nothing else.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    },
                ],
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "captcha_result",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "result": {
                            "type": "string",
                            "description": "The recognized captcha text",
                        }
                    },
                    "required": ["result"],
                    "additionalProperties": False,
                },
            },
        },
    }

    try:
        response = requests.post(
            OPENROUTER_API_URL, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        result = json.loads(content)
        return result.get("result")
    except Exception as e:
        print(f"Captcha recognition failed: {e}")
        return None
