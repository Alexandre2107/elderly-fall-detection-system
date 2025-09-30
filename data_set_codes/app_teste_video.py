import cv2
import mediapipe as mp
import time
import numpy as np

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.2, min_tracking_confidence=0.2)
mp_drawing = mp.solutions.drawing_utils

VIDEO_SOURCE = "data_set_videos/fall-02-cam0.mp4"  # caminho do vídeo   
cap = cv2.VideoCapture(VIDEO_SOURCE)

previous_y = None
fall_confirmed = False
time_fallen_start = None
print("=== SISTEMA DE DETECÇÃO DE QUEDAS ===")
print(f"Analisando vídeo: {VIDEO_SOURCE}")
print("O sistema irá analisar o vídeo e pausar no final até detectar uma queda.")
print("Pressione 'q' para sair manualmente.")
print("==========================================\n")

# Parâmetros (ajustados para melhor detecção)
Y_VELOCITY_THRESHOLD = 5         # velocidade mínima (reduzido para detectar melhor)
FALL_CONFIRM_TIME = 1.0          # tempo para confirmar queda (reduzido)
TRUNK_HORIZONTAL_THRESHOLD = 35  # ângulo tronco (reduzido)
LEG_HORIZONTAL_THRESHOLD = 35    # ângulo perna (reduzido)
LOWER_BODY_THRESHOLD = 0.65      # altura do quadril (reduzido)
HEAD_LOW_THRESHOLD = 0.7         # altura da cabeça (reduzido)

def calculate_angle(a, b):
    a = np.array(a); b = np.array(b)
    cosang = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    return np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))

last_frame = None
video_ended = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        if last_frame is not None:
            # Usar o último frame quando o vídeo terminar
            frame = last_frame.copy()
            if not video_ended:
                print("Vídeo terminou - analisando último frame até detectar queda...")
                video_ended = True
        else:
            break
    else:
        # Armazenar o frame atual como último frame válido
        last_frame = frame.copy()

    # Reduz resolução para ganhar FPS
    frame = cv2.resize(frame, (640, 360))
    h, w, _ = frame.shape

    # Converter para RGB para processamento MediaPipe
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    
    # Usar o frame original como base (não fundo preto)
    image = frame.copy()

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        lm = results.pose_landmarks.landmark

        # pontos chave
        hip = lm[mp_pose.PoseLandmark.RIGHT_HIP]
        shoulder = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        knee = lm[mp_pose.PoseLandmark.RIGHT_KNEE]
        ankle = lm[mp_pose.PoseLandmark.RIGHT_ANKLE]
        nose = lm[mp_pose.PoseLandmark.NOSE]

        hip_y = hip.y * h
        shoulder_y = shoulder.y * h
        nose_y = nose.y * h

        # velocidade (com suavização para reduzir ruído)
        if previous_y is not None:
            y_velocity = abs(hip_y - previous_y)  # usar valor absoluto
        else:
            y_velocity = 0
        previous_y = hip_y

        # ângulos
        trunk_vector = [(shoulder.x - hip.x), (shoulder.y - hip.y)]
        vertical_vector = [0, -1]
        trunk_angle = calculate_angle(trunk_vector, vertical_vector)

        leg_vector = [(ankle.x - knee.x), (ankle.y - knee.y)]
        leg_angle = calculate_angle(leg_vector, vertical_vector)

        # condições de queda
        is_fast_drop = y_velocity > Y_VELOCITY_THRESHOLD
        is_low_posture = hip.y > LOWER_BODY_THRESHOLD
        is_trunk_horizontal = trunk_angle > TRUNK_HORIZONTAL_THRESHOLD
        is_leg_horizontal = leg_angle > LEG_HORIZONTAL_THRESHOLD
        is_head_low = nose_y > HEAD_LOW_THRESHOLD * h
        
        # Lógica melhorada: queda detectada se há movimento rápido E posição baixa
        fall_detected = (is_fast_drop and is_low_posture) or (is_low_posture and is_trunk_horizontal and is_head_low)
        
        # queda possível
        if fall_detected:
            if time_fallen_start is None:
                time_fallen_start = time.time()
                print(f"Possível queda detectada! Vel: {y_velocity:.1f}, Hip Y: {hip.y:.2f}, Trunk: {trunk_angle:.1f}°")
        else:
            if time_fallen_start is not None:
                print("Posição normalizada")
            time_fallen_start = None
            fall_confirmed = False

        if time_fallen_start is not None:
            if time.time() - time_fallen_start > FALL_CONFIRM_TIME:
                fall_confirmed = True

        # Informações de debug com fundo para melhor legibilidade
        cv2.rectangle(image, (10, 10), (350, 150), (0, 0, 0), -1)
        cv2.putText(image, f"Vel: {y_velocity:.1f}", (20,30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        cv2.putText(image, f"Tronco: {trunk_angle:.1f}°", (20,50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)
        cv2.putText(image, f"Perna: {leg_angle:.1f}°", (20,70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
        cv2.putText(image, f"Hip Y: {hip.y:.2f}", (20,90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,255), 2)
        cv2.putText(image, f"Head Y: {nose.y:.2f}", (20,110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,100,100), 2)
        
        # Mostrar status do vídeo
        if video_ended:
            cv2.putText(image, "ANALISANDO ULTIMO FRAME", (20,130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

        # Status principal
        if fall_confirmed:
            cv2.rectangle(image, (50, 160), (350, 210), (0, 0, 255), -1)
            cv2.putText(image, "QUEDA CONFIRMADA!", (60,190), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 3)
            print("ALERTA: QUEDA CONFIRMADA!")
            
            # Mostrar a tela por mais alguns segundos antes de sair
            cv2.imshow("Fall Detection Pose", image)
            cv2.waitKey(3000)  # Aguarda 3 segundos
            print("Sistema finalizando após detecção de queda...")
            break  # Sai do loop quando queda é confirmada
            
        elif time_fallen_start:
            elapsed = time.time() - time_fallen_start
            cv2.rectangle(image, (50, 160), (350, 210), (0, 165, 255), -1)
            cv2.putText(image, f"Caindo... {elapsed:.1f}s", (60,190), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2)
        else:
            cv2.rectangle(image, (50, 160), (200, 200), (0, 255, 0), -1)
            cv2.putText(image, "Estavel", (60,185), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)

    cv2.imshow("Fall Detection Pose", image)
    
    # Permite sair com 'q' ou automaticamente quando queda é detectada
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("Sistema finalizado pelo usuário...")
        break

cap.release()
cv2.destroyAllWindows()
