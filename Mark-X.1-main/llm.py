import os
import json
import requests
import sys
from pathlib import Path

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "arcee-ai/trinity-large-preview:free"

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR = get_base_dir()

PROMPT_PATH = BASE_DIR / "core" / "prompt.txt"
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"

def load_api_keys() -> dict:
    if not os.path.exists(API_CONFIG_PATH):
        return {}

    try:
        with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ api_keys.json dosyası okunamadı: {e}")
        return {}


def get_openrouter_key() -> str | None:
    keys = load_api_keys()
    return keys.get("openrouter_api_key")

def load_system_prompt() -> str:
    try:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ prompt.txt yüklenemedi: {e}")
        return "Sen Jarvis'sin, yardımcı bir yapay zeka asistanısın."


SYSTEM_PROMPT = load_system_prompt()

def safe_json_parse(text: str) -> dict | None:
    if not text:
        return None

    text = text.strip()

    if "```json" in text:
        try:
            start = text.index("```json") + 7
            end = text.index("```", start)
            text = text[start:end].strip()
        except:
            pass
    elif "```" in text:
        try:
            start = text.index("```") + 3
            end = text.index("```", start)
            text = text[start:end].strip()
        except:
            pass

    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except Exception as e:
        print(f"⚠️ JSON ayrıştırma hatası: {e}")
        print(f"⚠️ Ham metin önizlemesi: {text[:200]}")
        return None

def get_llm_output(user_text: str, memory_block: dict | None = None) -> dict:

    if not user_text or not user_text.strip():
        return {
            "intent": "chat",
            "parameters": {},
            "needs_clarification": False,
            "text": "Efendim, ne dediğinizi tam olarak anlayamadım.",
            "memory_update": None
        }

    api_key = get_openrouter_key()
    if not api_key:
        print("❌ OPENROUTER API ANAHTARI BULUNAMADI")
        return {
            "intent": "chat",
            "parameters": {},
            "needs_clarification": False,
            "text": "Efendim, OpenRouter API anahtarı sisteme tanımlı değil.",
            "memory_update": None
        }

    memory_str = ""
    if memory_block:
        memory_str = "\n".join(f"{k}: {v}" for k, v in memory_block.items())

    user_prompt = f"""Kullanıcı mesajı: "{user_text}"

Bilinen kullanıcı belleği:
{memory_str if memory_str else "Kayıtlı bellek bulunmuyor."}"""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Jarvis-Asistan"
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ OpenRouter API Hatası: {response.text}")
            return {
                "intent": "chat",
                "parameters": {},
                "needs_clarification": False,
                "text": f"Efendim, API tarafında bir sorunla karşılaştım (Hata kodu: {response.status_code}).",
                "memory_update": None
            }

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        parsed = safe_json_parse(content)

        if parsed:
            return {
                "intent": parsed.get("intent", "chat"),
                "parameters": parsed.get("parameters", {}),
                "needs_clarification": parsed.get("needs_clarification", False),
                "text": parsed.get("text"),
                "memory_update": parsed.get("memory_update")
            }

        return {
            "intent": "chat",
            "parameters": {},
            "needs_clarification": False,
            "text": content,
            "memory_update": None
        }

    except requests.exceptions.Timeout:
        print("❌ OpenRouter zaman aşımı")
        return {
            "intent": "chat",
            "parameters": {},
            "needs_clarification": False,
            "text": "Efendim, sunucudan yanıt gelmedi, istek zaman aşımına uğradı.",
            "memory_update": None
        }

    except Exception as e:
        print(f"❌ YAPAY ZEKA HATASI: {e}")
        return {
            "intent": "chat",
            "parameters": {},
            "needs_clarification": False,
            "text": "Efendim, sistemde beklenmedik bir hata oluştu.",
            "memory_update": None
        }