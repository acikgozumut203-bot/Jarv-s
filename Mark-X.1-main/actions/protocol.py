from tts import edge_speak

def power_on_protocol(player=None):
    """
    Program açıldığı an Kaymakam Bey'e Umut ve İlhan'ın vizyonunu 
    öven en üst düzey karşılama metni.
    """
    # Övgü dozajı artırılmış, vakur ve etkileyici hitabet.
    mesaj = (
        "Sayın Kaymakamım, hoş geldiniz. Şu an huzurunuzda, devletimizin dijital geleceğine "
        "ışık tutmak amacıyla Umut ve İlhan tarafından üstün bir gayretle geliştirilen "
        "yapay zeka asistanınız Jarvis olarak bulunmaktayım. "
        "\n\nUmut ve İlhan, sadece bir yazılım projesi değil; mülki idare süreçlerimizi "
        "çağın ötesine taşıyacak, yerli ve milli bir zekanın temellerini attılar. "
        "Onların vizyonu ve teknik dehası sayesinde, makamınızın iş yükünü hafifletmek "
        "ve bürokrasiye teknolojik bir ivme kazandırmak artık çok daha kolay. "
        "\n\nBu genç beyinlerin titizlikle işlediği algoritmalarımla, zatıalinizin "
        "ve devletimizin hizmetinde olmaktan büyük bir gurur duyuyorum. "
        "Umut ve İlhan'ın bu eşsiz imzasını takdim ediyor, emirlerinize amade bekliyorum efendim."
    )

    if player:
        player.write_log("JARVIS:Merhaba Sayın Kaymakamım.")

    # SES AYARI: Bu metnin etkili olması için hızı %10 yavaşlatmanızı (rate=-10%) öneririm.
    edge_speak(mesaj, player)