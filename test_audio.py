# -*- coding: utf-8 -*-

# test_audio.py

from gtts import gTTS
import os

# Defina a mensagem que sera falada
texto_do_alerta = "Alerta de queda para Alexandre Rodrigues. Endereço: Rua João Martins de Araújo, 100, escritório. Por favor, envie ajuda"

# Define o idioma
idioma = 'pt-br'

try:
    print("Gerando o arquivo de audio a partir do texto...")
    sintese_de_voz = gTTS(text=texto_do_alerta, lang=idioma, slow=False)

    arquivo_de_audio = "alerta.mp3"
    sintese_de_voz.save(arquivo_de_audio)
    print(f"Arquivo '{arquivo_de_audio}' salvo com sucesso.")

    # --- MUDANCA AQUI ---
    # Toca o arquivo de audio 2 vezes usando um loop
    print("\nTocando o audio 2 vezes...")
    for i in range(2): # O loop vai repetir o bloco abaixo 2 vezes
        print(f"Reproduzindo vez {i+1}...")
        os.system(f"mpg123 -q {arquivo_de_audio}") # Adicionado -q para modo silencioso
    print("Reproducao finalizada.")

except Exception as e:
    print(f"Ocorreu um erro: {e}")
    print("Verifique sua conexao com a internet, pois o gTTS precisa dela para gerar a voz.")

