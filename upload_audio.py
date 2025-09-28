# upload_audio.py - Versao com ativacao de drive

import serial
import time
import os

# --- CONFIGURACOES ---
porta_serial = "/dev/serial0"
nome_arquivo_local = "alerta.wav"
nome_arquivo_remoto = "alerta.wav" 

# --- INICIALIZACAO DA PORTA SERIAL ---
try:
    ser = serial.Serial(porta_serial, baudrate=115200, timeout=2)
    print(f"Porta serial {porta_serial} aberta.")
except serial.SerialException as e:
    print(f"Erro ao abrir a porta serial: {e}")
    exit()

def enviar_comando_at(comando, resposta_esperada="OK", timeout=2):
    print(f"Enviando: {comando}")
    ser.write((comando + '\r\n').encode())
    time.sleep(timeout)
    resposta = ser.read_all().decode(errors='ignore').strip()
    print(f"Resposta: {resposta}")
    return resposta_esperada in resposta

# --- LOGICA PRINCIPAL DO UPLOAD ---
if __name__ == "__main__":
    if not os.path.exists(nome_arquivo_local):
        print(f"ERRO: O arquivo '{nome_arquivo_local}' nao foi encontrado.")
        ser.close()
        exit()

    if not enviar_comando_at("AT"):
        print("Falha na comunicacao com o modulo.")
        ser.close()
        exit()
    
    # <<< NOVO PASSO CRITICO >>>
    # Seleciona o drive de memoria flash (0) como o drive ativo.
    if not enviar_comando_at("AT+FSDRIVE=0"):
        print("ERRO: Nao foi possivel selecionar o drive de memoria do modulo.")
        ser.close()
        exit()

    tamanho_do_arquivo = os.path.getsize(nome_arquivo_local)
    print(f"Tamanho do arquivo '{nome_arquivo_local}': {tamanho_do_arquivo} bytes.")

    enviar_comando_at(f'AT+FSDEL={nome_arquivo_remoto}')
    
    if not enviar_comando_at(f'AT+FSWRITE={nome_arquivo_remoto},0,{tamanho_do_arquivo},10', "CONNECT"):
        print("ERRO: Modulo nao respondeu ao comando de escrita de arquivo.")
        ser.close()
        exit()
        
    print(f"Enviando os {tamanho_do_arquivo} bytes do arquivo. Aguarde...")
    with open(nome_arquivo_local, 'rb') as f:
        dados_do_arquivo = f.read()
        ser.write(dados_do_arquivo)

    time.sleep(5)
    resposta_final = ser.read_all().decode(errors='ignore').strip()
    print(f"Resposta final do modulo: {resposta_final}")

    if "OK" in resposta_final:
        print("\n>>> SUCESSO! O arquivo de audio foi enviado para a memoria do modulo.")
    else:
        print("\n>>> FALHA! Ocorreu um erro durante a transferencia do arquivo.")

    ser.close()
    print("Processo finalizado.")
