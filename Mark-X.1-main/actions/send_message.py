import time
import pyautogui
from tts import edge_speak

# Gerekli parametreler
REQUIRED_PARAMS = ["receiver", "message_text", "platform"]

def send_message(parameters: dict, response: str | None = None, player=None, session_memory=None) -> bool:
    """
    Windows uygulamaları (WhatsApp, Telegram vb.) üzerinden mesaj gönderir.

    Çok adımlı destek: Eksik parametreleri geçici bellek kullanarak sorar.

    Beklenen parametreler:
        - receiver (alıcı)
        - message_text (mesaj metni)
        - platform (platform, varsayılan: "WhatsApp")
    """

    if session_memory is None:
        msg = "Oturum belleği eksik, işleme devam edilemiyor."
        if player:
            player.write_log(msg)
        edge_speak(msg, player)
        return False

    if parameters:
        session_memory.update_parameters(parameters)

    # Eksik parametre kontrolü ve soru sorma aşaması
    for param in REQUIRED_PARAMS:
        value = session_memory.get_parameter(param)
        if not value:
        
            session_memory.set_current_question(param)
            question_text = ""
            if param == "receiver":
                question_text = "Efendim, mesajı kime göndermeliyim?"
            elif param == "message_text":
                question_text = "Efendim, ne söylememi istersiniz?"
            elif param == "platform":
                question_text = "Efendim, hangi platformu kullanmalıyım? (WhatsApp, Telegram vb.)"
            else:
                question_text = f"Efendim, lütfen şu bilgiyi verin: {param}."

            if player:
                player.write_log(f"Asistan: {question_text}")
            edge_speak(question_text, player)
            return False  

    # Tüm bilgiler tamamsa değişkenleri ata
    receiver = session_memory.get_parameter("receiver").strip()
    platform = session_memory.get_parameter("platform").strip() or "WhatsApp"
    message_text = session_memory.get_parameter("message_text").strip()

    if response:
        if player:
            player.write_log(response)
        edge_speak(response, player)

    try:
        pyautogui.PAUSE = 0.1

        # Uygulamayı ara ve aç
        pyautogui.press("win")
        time.sleep(0.3)
        pyautogui.write(platform, interval=0.03)
        pyautogui.press("enter")
        time.sleep(0.6)

        # Kişiyi bul (Ctrl+F genelde mesajlaşma uygulamalarında arama açar)
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.2)
        pyautogui.write(receiver, interval=0.03)
        time.sleep(0.2)
        pyautogui.press("enter")
        time.sleep(0.2)

        # Mesajı yaz ve gönder
        pyautogui.write(message_text, interval=0.03)
        pyautogui.press("enter")

        # İşlem bitince belleği temizle
        session_memory.clear_current_question()
        session_memory.clear_pending_intent()
        session_memory.update_parameters({})  

        # Başarı mesajı
        success_msg = f"Efendim, mesajınız {platform} üzerinden {receiver} kişisine gönderildi."
        if player:
            player.write_log(success_msg)
        edge_speak(success_msg, player)

        return True

    except Exception as e:
        msg = f"Efendim, mesaj gönderilirken bir hata oluştu. ({e})"
        if player:
            player.write_log(msg)
        edge_speak(msg, player)
        return False