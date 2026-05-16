# app/services/audio_service.py

from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts


VOICES = {
    # Chinese
    "Xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "Yunxi": "zh-CN-YunxiNeural",
    "Yunyang": "zh-CN-YunyangNeural",
    "Xiaoyi": "zh-CN-XiaoyiNeural",

    # Backward compatibility
    "晓晓": "zh-CN-XiaoxiaoNeural",
    "云希": "zh-CN-YunxiNeural",
    "云扬": "zh-CN-YunyangNeural",
    "晓伊": "zh-CN-XiaoyiNeural",

    # English
    "Ava": "en-US-AvaNeural",
    "Jenny": "en-US-JennyNeural",
    "Guy": "en-US-GuyNeural",
    "Brian": "en-US-BrianNeural",

    # French
    "Denise": "fr-FR-DeniseNeural",
    "Henri": "fr-FR-HenriNeural",

    # Spanish
    "Elvira": "es-ES-ElviraNeural",
    "Alvaro": "es-ES-AlvaroNeural",

    # Russian
    "Svetlana": "ru-RU-SvetlanaNeural",
    "Dmitry": "ru-RU-DmitryNeural",

    # Arabic
    "Zariyah": "ar-SA-ZariyahNeural",
    "Hamed": "ar-SA-HamedNeural",
}


DEFAULT_VOICE_BY_LANGUAGE = {
    "en": "en-US-AvaNeural",
    "zh": "zh-CN-XiaoxiaoNeural",
    "fr": "fr-FR-DeniseNeural",
    "es": "es-ES-ElviraNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "ar": "ar-SA-ZariyahNeural",
}


BACKEND_AUDIO_DIR = Path("output/audio").resolve()
BACKEND_AUDIO_DIR.mkdir(parents=True, exist_ok=True)


async def _generate_audio_async(text: str, voice: str, output_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def normalize_output_language(output_language: str | None) -> str:
    value = (output_language or "en").strip().lower()

    aliases = {
        "english": "en",
        "chinese": "zh",
        "french": "fr",
        "spanish": "es",
        "russian": "ru",
        "arabic": "ar",
        "英文": "en",
        "中文": "zh",
        "法语": "fr",
        "西班牙语": "es",
        "俄语": "ru",
        "阿拉伯语": "ar",
    }

    value = aliases.get(value, value)

    if value not in {"en", "zh", "fr", "es", "ru", "ar"}:
        return "en"

    return value


def resolve_voice(voice_name: str | None, output_language: str | None = "en") -> str:
    language = normalize_output_language(output_language)

    if voice_name and voice_name in VOICES:
        return VOICES[voice_name]

    return DEFAULT_VOICE_BY_LANGUAGE.get(language, "en-US-AvaNeural")


def generate_backend_audio(
        text: str,
        task_id: str,
        voice_name: str = "Ava",
        output_language: str = "en",
) -> str:
    if not text or not text.strip():
        raise ValueError("Audio generation failed: text content is empty.")

    language = normalize_output_language(output_language)
    voice = resolve_voice(voice_name, language)

    safe_task_id = "".join(
        c for c in task_id
        if c.isalnum() or c in ("-", "_")
    )

    if not safe_task_id:
        safe_task_id = "audio"

    audio_filename = f"{safe_task_id}_{language}.mp3"
    output_path = BACKEND_AUDIO_DIR / audio_filename

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(
            _generate_audio_async(text, voice, str(output_path))
        )
    finally:
        loop.close()

    return f"/agent/backend-audio/{audio_filename}"