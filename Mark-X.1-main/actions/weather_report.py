import webbrowser
from urllib.parse import quote_plus
from tts import edge_speak


def weather_action(
    parameters: dict,
    player=None,
    session_memory=None
):
    """
    Hava durumu raporu eylemi.
    Google hava durumu aramasını açar ve kısa bir sesli onay verir.
    """

    city = parameters.get("city")
    time = parameters.get("time")
    
    # Şehir bilgisi eksikse
    if not city or not isinstance(city, str):
        msg = "Efendim, hava durumu raporu için şehir bilgisi eksik."
        _speak_and_log(msg, player)
        return msg

    city = city.strip()

    # Zaman bilgisi yoksa varsayılan olarak "bugün" ayarlanır
    if not time or not isinstance(time, str):
        time = "bugün"
    else:
        time = time.strip()

    # Arama sorgusunu Türkçe olacak şekilde ayarla
    search_query = f"{city} {time} hava durumu"
    encoded_query = quote_plus(search_query)
    url = f"https://www.google.com/search?q={encoded_query}"

    try:
        webbrowser.open(url)
    except Exception:
        msg = "Efendim, hava durumu raporu için tarayıcıyı açamadım."
        _speak_and_log(msg, player)
        return msg

    # Başarı mesajı
    msg = f"Efendim, {city} için {time} hava durumu bilgilerini getiriyorum."
    _speak_and_log(msg, player)

    if session_memory:
        try:
            session_memory.set_last_search(
                query=search_query,
                response=msg
            )
        except Exception:
            pass  

    return msg


def _speak_and_log(message: str, player=None):
    """Yardımcı Fonksiyon: Günlük kaydı ve sesli yanıt"""
    if player:
        try:
            player.write_log(f"Asistan: {message}")
        except Exception:
            pass

    try:
        edge_speak(message)
    except Exception:
        pass