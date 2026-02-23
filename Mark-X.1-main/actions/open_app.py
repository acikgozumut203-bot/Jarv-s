import time
import pyautogui
from tts import edge_speak


def open_app(
    parameters: dict,
    response: str | None = None,
    player=None,
    session_memory=None
) -> bool:
    """
    Windows aramayı kullanarak bir uygulama açar.

    parametreler:
        - app_name (str)

    Bellek davranışı:
        - YALNIZCA oturum belleğini kullanır
        - Uzun süreli belleğe yazma yapmaz
    """

    app_name = (parameters or {}).get("app_name", "").strip()

    if not app_name and session_memory:
        app_name = session_memory.open_app or ""

    if not app_name:
        msg = "Efendim, hangi uygulamayı açmam gerektiğini belirleyemedim."
        if player:
            player.write_log(msg)
        edge_speak(msg, player)
        return False

    if response:
        if player:
            player.write_log(response)
        edge_speak(response, player)

    try:
        pyautogui.PAUSE = 0.1

        # Windows tuşuna bas ve bekle
        pyautogui.press("win")
        time.sleep(0.3)

        # Uygulama adını yaz
        pyautogui.write(app_name, interval=0.03)
        time.sleep(0.2)

        # Enter'a bas
        pyautogui.press("enter")
        time.sleep(0.6)

        if session_memory:
            session_memory.set_open_app(app_name)

        return True

    except Exception as e:
        msg = f"Efendim, {app_name} uygulamasını açarken bir sorunla karşılaştım."
        if player:
            player.write_log(f"{msg} ({e})")
        edge_speak(msg, player)
        return False