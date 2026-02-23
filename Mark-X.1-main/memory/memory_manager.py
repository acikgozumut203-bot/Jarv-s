# memory/memory_manager.py
import json
import os
from threading import Lock
from datetime import datetime

MEMORY_PATH = "memory/memory.json"
_lock = Lock()  # Aynı anda birden fazla işlemin dosyayı bozmasını engeller


def _empty_memory() -> dict:
    """Boş bir bellek yapısı döndürür."""
    return {
        "identity": {},        # Kimlik bilgileri (isim, yaş vb.)
        "preferences": {},     # Tercihler (sevdiği renkler, müzikler vb.)
        "relationships": {},   # İlişkiler (arkadaşlar, aile vb.)
        "emotional_state": {}  # Duygusal durum
    }


def load_memory() -> dict:
    """Belleği diskten yükler; dosya yoksa veya geçersizse boş bellek döndürür."""
    if not os.path.exists(MEMORY_PATH):
        return _empty_memory()

    with _lock:
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                return _empty_memory()
        except Exception:
            return _empty_memory()


def save_memory(memory: dict) -> None:
    """Belleği güvenli bir şekilde diske kaydeder."""
    if not isinstance(memory, dict):
        return

    os.makedirs(os.path.dirname(MEMORY_PATH), exist_ok=True)

    with _lock:
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            # ensure_ascii=False kullanarak Türkçe karakterlerin düzgün kaydedilmesini sağlıyoruz
            json.dump(memory, f, indent=2, ensure_ascii=False)


def _recursive_update(target: dict, updates: dict) -> bool:
    """Güncellemeleri ana bellekle özyinelemeli olarak birleştirir. Değişiklik varsa True döner."""
    changed = False

    for key, value in updates.items():
        # Geçersiz veya boş değerleri atla
        if value is None or (isinstance(value, str) and not value.strip()):
            continue

        if isinstance(value, dict) and "value" not in value:
            if key not in target or not isinstance(target[key], dict):
                target[key] = {}
                changed = True
            if _recursive_update(target[key], value):
                changed = True
        else:
            # Yeni bilgiyi sözlük yapısında sakla
            entry = value if isinstance(value, dict) and "value" in value else {"value": value}
            if key not in target or target[key] != entry:
                target[key] = entry
                changed = True

    return changed


def update_memory(memory_update: dict) -> dict:
    """Yapay zekadan gelen bellek güncellemesini ana belleğe işler ve kaydeder."""
    if not isinstance(memory_update, dict):
        return load_memory()

    memory = load_memory()
    if _recursive_update(memory, memory_update):
        save_memory(memory)

    return memory