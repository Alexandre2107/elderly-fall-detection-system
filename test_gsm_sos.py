# test_gsm_alerta_rapido.py

import serial
import time

# --- CONFIGURACOES ---
numero_destino = "+5535999092107" # EDITE com o seu numero
porta_serial = "/dev/serial0"

# --- INICIALIZACAO DA PORTA SERIAL ---
try:
    ser = serial.Serial(porta_serial, baudrate=115200, timeout=1)
    print(f"Porta serial {porta_serial} aberta.")
except serial.SerialException as e:
    print(f"Erro ao abrir a porta serial: {e}")
    exit()

def enviar_comando_at(comando, resposta_esperada="OK", timeout=0.2):
    """Envia um comando AT e retorna True se a resposta for a esperada."""
    ser.write((comando + '\r\n').encode())
    # Um tempo de espera menor para comandos rapidos
    time.sleep(timeout) 
    resposta = ser.read_all().decode(errors='ignore').strip()
    # Nao vamos imprimir a resposta para nao poluir o terminal com os bipes
    return resposta_esperada in resposta

# --- NOVA FUNCAO DE CHAMADA ---
def fazer_chamada_com_alerta_rapido(numero):
    print("\n--- Iniciando chamada de alerta rapido ---")
    if not enviar_comando_at(f"ATD{numero};", "OK", timeout=5):
        print(">>> Falha ao iniciar a chamada.")
        return False
    
    print(">>> Chamada iniciada. Aguardando 5 segundos para a pessoa atender...")
    time.sleep(5)
    
    # Gera um alerta rapido por 20 segundos
    print(">>> Enviando tons de alerta rapido...")
    tempo_final = time.time() + 20 # Duracao total do alerta
    while time.time() < tempo_final:
        # AT+VTS="#" e o comando para tocar o tom do Jogo da Velha (agudo)
        enviar_comando_at('AT+VTS="#"') 
        time.sleep(0.2) # Pausa curta para criar um efeito de sirene
        
    print(">>> Alerta finalizado.")
    
    # Encerra a chamada
    if enviar_comando_at("ATH", "OK", timeout=2):
        print(">>> Chamada encerrada com sucesso.")
    else:
        print(">>> Falha ao encerrar a chamada.")
    return True


# --- EXECUCAO DO TESTE ---
if __name__ == "__main__":
    if enviar_comando_at("AT", timeout=2):
        print("\nConexao com o modulo SIM800L bem-sucedida!")
        fazer_chamada_com_alerta_rapido(numero_destino)
    else:
        print("\nFalha na comunicacao com o modulo.")
    
    ser.close()
    print("\nTeste finalizado.")
