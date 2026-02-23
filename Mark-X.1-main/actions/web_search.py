import re
from serpapi import GoogleSearch
from tts import edge_speak
from memory.config_manager import get_serpapi_key

MAX_NEWS_ITEMS = 3  # Maksimum haber sayısı

def clean(text: str) -> str:
    """Metni temizler: gereksiz boşlukları ve parantez içlerini kaldırır."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\(.*?\)|\[.*?\]", "", text)
    text = text.strip()
    text = re.sub(r"\.{2,}", ".")
    text = re.sub(r"\s*—\s*", " - ", text)
    return text

def is_trash(text: str) -> bool:
    """Reklam, borsa veya spam içerikli metinleri tespit eder."""
    t = text.lower()
    trash_patterns = [
        r"\bstock(?:s)?\b.*\btoday\b",
        r"\bshare(?:s)?\b.*\bprice\b",
        r"\binvestor(?:s)?\b",
        r"\btrading\b",
        r"\bmarket(?:s)?\b.*\bopen(?:s|ed)?\b",
        r"\bticker\b",
        r"\bnyse\b",
        r"\bnasdaq\b",
        r"\.\w{2,4}\sis\b",
    ]
    spam_keywords = [
        "click here", "read more", "advertisement", "sponsored",
        "subscribe", "newsletter", "sign up", "tıklayın", "devamı",
        "best things to do", "events this week", "calendar",
        "official website", "visit our", "learn more",
        "year in review", "trending now", "top 10"
    ]
    for pattern in trash_patterns:
        if re.search(pattern, t):
            return True
    return any(keyword in t for keyword in spam_keywords)

def extract_clean_news(result: dict) -> str:
    """Haber başlığını ve kısa özetini temiz bir şekilde birleştirir."""
    title = clean(result.get("title", ""))
    snippet = clean(result.get("snippet", ""))
    if not title:
        return ""
    if snippet.startswith(title[:30]) or snippet == title:
        return title
    if len(snippet) > 120:
        snippet = snippet[:120]
        last_period = snippet.rfind(".")
        last_space = snippet.rfind(" ")
        if last_period > 80:
            snippet = snippet[:last_period + 1]
        elif last_space > 80:
            snippet = snippet[:last_space] + "..."
        return f"{title}. {snippet}"
    return title

def format_news_output(news_items: list) -> str:
    """Haberleri Türkçe bağlaçlarla birleştirir."""
    if len(news_items) == 1:
        return news_items[0]
    elif len(news_items) == 2:
        return f"{news_items[0]}. Ayrıca, {news_items[1]}"
    else:
        result = news_items[0]
        for item in news_items[1:-1]:
            result += f". {item}"
        result += f". Ek olarak şunu da belirteyim, {news_items[-1]}"
        return result
    
def serpapi_search(query: str) -> str:
    """SerpAPI kullanarak Google News üzerinde arama yapar."""
    api_key = get_serpapi_key()
    if not api_key:
        return "Efendim, web arama sistemi yapılandırılmamış. API anahtarı eksik."

    clean_query = query
    # "Ne oldu" gibi soruları haber aramasına çevirir
    if "ne oldu" in query.lower() or "neler oldu" in query.lower():
        clean_query = re.sub(r"(?:ne oldu|neler oldu|hakkında bilgi ver)\s*", "", query, flags=re.IGNORECASE)
        clean_query += " haberleri"

    params = {
        "q": clean_query,
        "engine": "google_news",
        "hl": "tr",  # Türkçe sonuçlar için 'tr'
        "gl": "tr",  # Türkiye lokasyonu için 'tr'
        "num": 15
    }

    try:
        from serpapi import GoogleSearch as Client
        client = Client(params)
        data = client.get_dict()
        results = data.get("news_results", [])
    except Exception:
        # Haberlerde bulunamazsa genel Google araması dene
        params["engine"] = "google"
        try:
            client = Client(params)
            data = client.get_dict()
            results = data.get("organic_results", [])
        except Exception:
            return "Efendim, arama servisine bağlanırken bir sorun oluştu."

    if not results:
        return "Efendim, bununla ilgili güncel bir haber bulamadım."

    news_items = []
    for result in results:
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        if is_trash(title) or is_trash(snippet):
            continue
        news_text = extract_clean_news(result)
        if news_text and len(news_text.split()) >= 4:
            news_items.append(news_text)
        if len(news_items) >= MAX_NEWS_ITEMS:
            break

    if not news_items:
        return "Efendim, bazı sonuçlar buldum ancak net bir haber hikayesi çıkaramadım."

    return format_news_output(news_items)

def web_search(parameters, player=None, session_memory=None):
    """Ana fonksiyon: Arama yapar, log yazar ve seslendirir."""
    query = (parameters or {}).get("query", "").strip()
    if not query:
        msg = "Efendim, arama isteğinizi tam olarak anlayamadım."
        edge_speak(msg)
        return msg

    answer = serpapi_search(query)

    if player:
        player.write_log(f"Asistan: {answer}")

    edge_speak(answer)

    if session_memory:
        session_memory.set_last_search(query, answer)

    return answer