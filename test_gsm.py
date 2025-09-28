# -*- coding: utf-8 -*-
# test_gsm_com_audio.py - Script unificado

import serial
import time
from gtts import gTTS
import os

# --- CONFIGURACOES ---
numero_destino = "+5535999092107" # EDITE com o numero do seu celular
mensagem_sms = "ALERTA DE QUEDA: Ligando em seguida com uma mensagem de voz."
porta_serial = "/dev/serial0"
arquivo_de_audio = "alerta.mp3"

# Texto da mensagem de voz (com acentos corrigidos)
texto_do_alerta = "Olá, meu nome é Alexandre Rodrigues. Estou no endereço Rua João Martins de Araújo, Número 100, e estou caído no cômodo: escritório, não conseguindo levantar. Por favor, mande ajuda."

# --- INICIALIZACAO DA PORTA SERIAL ---
try:
    ser = serial.Serial(porta_serial, baudrate=115200, timeout=5)
    print(f"Porta serial {porta_serial} aberta com sucesso.")
except serial.SerialException as e:
    print(f"Erro ao abrir a porta serial: {e}")
    exit()

# --- NOVA FUNCAO PARA GERAR O AUDIO ---
def gerar_audio_de_alerta():
    """Gera o arquivo de audio a partir do texto, se ele nao existir."""
    if not os.path.exists(arquivo_de_audio):
        print("Gerando o arquivo de audio (isso so acontece uma vez)...")
        try:
            sintese_de_voz = gTTS(text=texto_do_alerta, lang='pt-br', slow=False)
            sintese_de_voz.save(arquivo_de_audio)
            print(f"Arquivo '{arquivo_de_audio}' salvo com sucesso.")
            return True
        except Exception as e:
            print(f"Falha ao gerar audio: {e}. Verifique a conexao com a internet.")
            return False
    else:
        print(f"Arquivo '{arquivo_de_audio}' ja existe. Usando o arquivo local.")
        return True

def enviar_comando_at(comando, resposta_esperada="OK", timeout=2):
    print(f"Enviando comando: {comando}")
    ser.write((comando + '\r\n').encode())
    time.sleep(timeout)
    resposta = ser.read_all().decode(errors='ignore').strip()
    print(f"Resposta do modulo: {resposta}")
    return resposta_esperada in resposta
    
# --- FUNCOES GSM (enviar_sms nao mudou) ---
def enviar_sms(numero, mensagem):
    # (Esta funcao permanece a mesma do script anterior)
    print("\n--- Tentando enviar SMS ---")
    if not enviar_comando_at("AT+CMGF=1"): return False
    if not enviar_comando_at(f'AT+CMGS="{numero}"', ">"): return False
    ser.write(mensagem.encode())
    time.sleep(0.5)
    ser.write(bytes([26]))
    time.sleep(5)
    resposta = ser.read_all().decode(errors='ignore')
    if "+CMGS:" in resposta:
        print(">>> SMS enviado com sucesso!")
        return True
    else:
        print(">>> Falha ao enviar SMS.")
        return False

# --- FUNCAO FAZER_CHAMADA ATUALIZADA ---
def fazer_chamada_com_audio(numero):
    print("\n--- Tentando fazer chamada com audio ---")
    if not enviar_comando_at(f"ATD{numero};", "OK", timeout=5):
        print(">>> Falha ao iniciar a chamada.")
        return False
    
    print(">>> Chamada iniciada. Aguardando 5 segundos para a pessoa atender...")
    time.sleep(5)
    
    # Toca a mensagem de audio 2 vezes
    print(">>> Tocando a mensagem de alerta...")
    for i in range(2):
        print(f"Reproduzindo vez {i+1}...")
        os.system(f"mpg123 -q {arquivo_de_audio}")
        time.sleep(1) # Pequena pausa entre as repeticoes
        
    print(">>> Mensagem finalizada.")
    
    # Encerra a chamada
    if enviar_comando_at("ATH", "OK"):
        print(">>> Chamada encerrada com sucesso.")
    else:
        print(">>> Falha ao encerrar a chamada.")
    return True


# --- EXECUCAO DO TESTE ---
if __name__ == "__main__":
    # 1. Gera o audio (se necessario)
    if not gerar_audio_de_alerta():
        ser.close()
        exit()

    # 2. Testa a conexao com o modulo
    if enviar_comando_at("AT"):
        print("\n>>> Conexao com o modulo SIM800L bem-sucedida!")
        
        # 3. Envia o SMS de aviso
        # if enviar_sms(numero_destino, mensagem_sms):
            
            # 4. Espera um pouco e faz a chamada com a mensagem
        print("\nAguardando 5 segundos antes de fazer a chamada...")
        time.sleep(5)
        fazer_chamada_com_audio(numero_destino)
            
    else:
        print("\n>>> Falha na comunicacao com o modulo. Verifique as conexoes e a alimentacao.")
    
    ser.close()
    print("\nTeste finalizado. Porta serial fechada.")
