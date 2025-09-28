
from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import time
import numpy as np
import math
import serial
import psutil
import os    

app = Flask(__name__)

# --- INICIALIZACAO DO PROCESSO PARA METRICAS ---
process = psutil.Process(os.getpid())

# --- CONFIGURACAO DO MEDIAPIPE ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.6, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils

# --- CONFIGURACAO DA CAMERA ---
def find_camera_index():
    for index in range(15):
        cap_test = cv2.VideoCapture(index)
        if cap_test.isOpened():
            print(f"Camera funcional encontrada no indice {index}")
            cap_test.release(); return index
    return -1

camera_index = find_camera_index()
if camera_index == -1: exit("Erro: Nenhuma camera foi encontrada.")
cap = cv2.VideoCapture(camera_index)


# --- SECAO GSM ---
numero_alerta = "+5535999092107"
porta_serial_gsm = "/dev/serial0"
try:
    ser_gsm = serial.Serial(porta_serial_gsm, baudrate=115200, timeout=5)
    print(f"Porta serial GSM {porta_serial_gsm} aberta.")
except serial.SerialException as e:
    print(f"ERRO CRITICO: Nao foi possivel abrir a porta serial GSM: {e}")
    ser_gsm = None

def enviar_comando_at(comando, resposta_esperada="OK", timeout=0.2):
    if ser_gsm is None: return False
    ser_gsm.write((comando + '\r\n').encode())
    time.sleep(timeout); resposta = ser_gsm.read_all().decode(errors='ignore').strip()
    return resposta_esperada in resposta

def enviar_sms(numero, mensagem, tempo_confirmacao):
    print("--- Acionando envio de SMS ---")
    if not enviar_comando_at("AT+CMGF=1", timeout=1): return
    if not enviar_comando_at(f'AT+CMGS="{numero}"', ">", timeout=5): return
    ser_gsm.write(mensagem.encode()); time.sleep(0.5); ser_gsm.write(bytes([26])); time.sleep(5)
    
    # <<< COLETA DE METRICA DE TEMPO >>>
    tempo_envio_sms = time.time()
    latencia_sms = tempo_envio_sms - tempo_confirmacao
    print(f"[METRICA] Latencia do Alerta SMS: {latencia_sms:.2f} segundos")
    print("--- SMS enviado ---")

def fazer_chamada_com_alerta_rapido(numero):
    print("--- Acionando chamada com alerta rapido ---")
    if not enviar_comando_at(f"ATD{numero};", "OK", timeout=5): return
    
    # <<< COLETA DE METRICA DE TEMPO >>>
    tempo_inicio_chamada = time.time()
    print(f"[METRICA] Chamada iniciada em: {tempo_inicio_chamada}")
    
    print(">>> Enviando tons de alerta rapido...")
    tempo_final = time.time() + 20
    while time.time() < tempo_final:
        enviar_comando_at('AT+VTS="#"'); time.sleep(0.2)
    
    enviar_comando_at("ATH", "OK", timeout=2)
    print("--- Chamada finalizada ---")
    
# --- Variaveis de estado ---
current_state = "Estavel"
fall_confirmed = False
previous_hip_y = None
time_unstable_start = None
high_velocity_event = False
was_previously_tracking = True
last_stable_hip_y = None

# --- Limiares ---
FALL_CONFIRM_TIME = 4.5
Y_VELOCITY_THRESHOLD = 20
TORSO_VERTICAL_THRESHOLD = 70
ASPECT_RATIO_UPRIGHT_THRESHOLD = 1.2

# --- Variavel para metricas de sistema ---
last_metric_time = time.time()

def generate_frames():
    global current_state, fall_confirmed, previous_hip_y, time_unstable_start, high_velocity_event
    global was_previously_tracking, last_stable_hip_y, last_metric_time

    while True:
        success, frame = cap.read()
        if not success: break
        
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        if results.pose_landmarks:
            is_reacquiring_track = not was_previously_tracking
            was_previously_tracking = True
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # ... (Toda a logica de deteccao de pose permanece a mesma)
            landmarks = results.pose_landmarks.landmark
            h, w, _ = frame.shape
            sh_l, sh_r = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER], landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            hip_l, hip_r = landmarks[mp_pose.PoseLandmark.LEFT_HIP], landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
            hip_mid_y = (hip_l.y + hip_r.y) / 2
            current_hip_y = int(hip_mid_y * h)

            if is_reacquiring_track and last_stable_hip_y is not None:
                y_velocity = current_hip_y - last_stable_hip_y
            else:
                y_velocity = current_hip_y - previous_hip_y if previous_hip_y is not None else 0
            
            if y_velocity > Y_VELOCITY_THRESHOLD:
                high_velocity_event = True
                current_state = "Caindo"
            previous_hip_y = current_hip_y

            torso_angle = abs(math.degrees(math.atan2((hip_l.y + hip_r.y)/2 - (sh_l.y + sh_r.y)/2, (hip_l.x + hip_r.x)/2 - (sh_l.x + sh_r.x)/2)))
            points = np.array([[lm.x * w, lm.y * h] for lm in landmarks]).astype(int)
            body_height = np.max(points, axis=0)[1] - np.min(points, axis=0)[1]
            body_width = np.max(points, axis=0)[0] - np.min(points, axis=0)[0]
            aspect_ratio = body_height / body_width if body_width > 0 else 0
            is_upright = torso_angle > TORSO_VERTICAL_THRESHOLD and aspect_ratio > ASPECT_RATIO_UPRIGHT_THRESHOLD

            if is_upright:
                current_state = "Estavel"
                time_unstable_start = None
                fall_confirmed = False
                high_velocity_event = False
                last_stable_hip_y = current_hip_y
            else:
                if high_velocity_event:
                    if time_unstable_start is None:
                        # <<< COLETA DE METRICA DE TEMPO >>>
                        time_unstable_start = time.time()
                        print(f"[METRICA] Evento de instabilidade iniciado em: {time_unstable_start}")
                        
                        current_state = "Instavel"
                        
            if current_state == "Instavel" and time_unstable_start is not None:
                if time.time() - time_unstable_start >= FALL_CONFIRM_TIME:
                    if not fall_confirmed:
                        # <<< COLETA DE METRICA DE TEMPO >>>
                        tempo_confirmacao = time.time()
                        tempo_total_deteccao = tempo_confirmacao - time_unstable_start
                        print(f"[METRICA] Queda confirmada em: {tempo_confirmacao}")
                        print(f"[METRICA] Tempo de Confirmacao da Queda: {tempo_total_deteccao:.2f} segundos")
                        
                        fall_confirmed = True
                        enviar_sms(numero_alerta, "ALERTA DE QUEDA! Alexandre Rodrigues esta caido no Escritorio", tempo_confirmacao)
                        fazer_chamada_com_alerta_rapido(numero_alerta)
        else:
            was_previously_tracking = False
            current_state = "Nenhuma pessoa detectada"
        
        # <<< COLETA DE METRICAS DE SISTEMA >>>
        if time.time() - last_metric_time > 5.0: # A cada 5 segundos
            cpu_usage = process.cpu_percent()
            ram_usage = process.memory_info().rss / (1024 * 1024) # em MB
            print(f"[METRICA] Uso de CPU: {cpu_usage:.2f}% | Uso de RAM: {ram_usage:.2f} MB")
            last_metric_time = time.time()
        
        # Logica de exibicao na tela... (sem alteracao)
        if fall_confirmed: cv2.putText(frame, "QUEDA CONFIRMADA!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 4)
        cv2.putText(frame, f"Estado: {current_state}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        if current_state == "Instavel" and time_unstable_start is not None:
             time_in_unstable_state = time.time() - time_unstable_start
             cv2.putText(frame, f"Tempo Instavel: {time_in_unstable_state:.1f}s", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# --- Rotas do Flask (sem alteracao) ---
@app.route('/')
def index(): return render_template('index.html')
@app.route('/video_feed')
def video_feed(): return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__ == '__main__': app.run(host='0.0.0.0', port=5000, debug=False)            
