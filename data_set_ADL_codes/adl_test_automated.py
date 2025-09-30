import cv2
import mediapipe as mp
import time
import numpy as np
import os
import csv
from datetime import datetime
import glob

class ADLFallDetectionTester:
    """
    Testador especializado para vídeos ADL (Activities of Daily Living)
    Estes vídeos NÃO devem ser detectados como quedas - são atividades normais
    """
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.2, min_tracking_confidence=0.2)
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Parâmetros de detecção (mesmos do sistema original)
        self.Y_VELOCITY_THRESHOLD = 8
        self.FALL_CONFIRM_TIME = 4.4
        self.TRUNK_HORIZONTAL_THRESHOLD = 45
        self.LEG_HORIZONTAL_THRESHOLD = 35
        self.LOWER_BODY_THRESHOLD = 0.75
        self.HEAD_LOW_THRESHOLD = 0.7
        
        # Timeout para análise do último frame
        self.MAX_LAST_FRAME_ANALYSIS_TIME = 10.0
        
    def calculate_angle(self, a, b):
        a = np.array(a)
        b = np.array(b)
        cosang = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))
    
    def analyze_adl_video(self, video_path, show_video=False):
        """
        Analisa um vídeo ADL e retorna os resultados
        IMPORTANTE: ADL videos NÃO devem ser detectados como quedas
        """
        video_name = os.path.basename(video_path)
        print(f"Analisando ADL: {video_name}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {
                'video': video_name,
                'video_type': 'ADL',
                'fall_detected': False,
                'false_positive': False,
                'error': 'Não foi possível abrir o vídeo',
                'detection_time': None,
                'total_frames': 0,
                'analysis_duration': 0
            }
        
        # Informações do vídeo
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        # Variáveis de controle
        previous_y = None
        fall_confirmed = False
        time_fallen_start = None
        last_frame = None
        video_ended = False
        
        analysis_start_time = time.time()
        last_frame_analysis_start = None
        frame_count = 0
        fall_detection_frame = None
        
        while cap.isOpened():
            ret, frame = cap.read()
            
            if not ret:
                if last_frame is not None:
                    frame = last_frame.copy()
                    if not video_ended:
                        print(f"  Vídeo ADL terminou - analisando último frame...")
                        video_ended = True
                        last_frame_analysis_start = time.time()
                    
                    if last_frame_analysis_start and (time.time() - last_frame_analysis_start) > self.MAX_LAST_FRAME_ANALYSIS_TIME:
                        print(f"  Timeout na análise do último frame ADL")
                        break
                else:
                    break
            else:
                last_frame = frame.copy()
                frame_count += 1
            
            # Reduzir resolução para processamento mais rápido
            frame = cv2.resize(frame, (640, 360))
            h, w, _ = frame.shape
            
            # Processar com MediaPipe
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_image)
            
            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                
                # Pontos chave
                hip = lm[self.mp_pose.PoseLandmark.RIGHT_HIP]
                shoulder = lm[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
                knee = lm[self.mp_pose.PoseLandmark.RIGHT_KNEE]
                ankle = lm[self.mp_pose.PoseLandmark.RIGHT_ANKLE]
                nose = lm[self.mp_pose.PoseLandmark.NOSE]
                
                hip_y = hip.y * h
                shoulder_y = shoulder.y * h
                nose_y = nose.y * h
                
                # Calcular velocidade
                if previous_y is not None:
                    y_velocity = abs(hip_y - previous_y)
                else:
                    y_velocity = 0
                previous_y = hip_y
                
                # Calcular ângulos
                trunk_vector = [(shoulder.x - hip.x), (shoulder.y - hip.y)]
                vertical_vector = [0, -1]
                trunk_angle = self.calculate_angle(trunk_vector, vertical_vector)
                
                leg_vector = [(ankle.x - knee.x), (ankle.y - knee.y)]
                leg_angle = self.calculate_angle(leg_vector, vertical_vector)
                
                # Condições de queda (mesma lógica do sistema original)
                is_fast_drop = y_velocity > self.Y_VELOCITY_THRESHOLD
                is_low_posture = hip.y > self.LOWER_BODY_THRESHOLD
                is_trunk_horizontal = trunk_angle > self.TRUNK_HORIZONTAL_THRESHOLD
                is_leg_horizontal = leg_angle > self.LEG_HORIZONTAL_THRESHOLD
                is_head_low = nose_y > self.HEAD_LOW_THRESHOLD * h
                
                # Lógica de detecção
                fall_detected = (is_fast_drop and is_low_posture) or (is_low_posture and is_trunk_horizontal and is_head_low)
                
                if fall_detected:
                    if time_fallen_start is None:
                        time_fallen_start = time.time()
                        print(f"    ⚠️ POSSÍVEL FALSO POSITIVO no frame {frame_count}! Vel: {y_velocity:.1f}, Hip Y: {hip.y:.2f}")
                else:
                    time_fallen_start = None
                    fall_confirmed = False
                
                # Confirmar "queda" (que seria um falso positivo)
                if time_fallen_start is not None:
                    if time.time() - time_fallen_start > self.FALL_CONFIRM_TIME:
                        fall_confirmed = True
                        fall_detection_frame = frame_count
                        print(f"    ❌ FALSO POSITIVO CONFIRMADO no frame {frame_count}!")
                        break
                
                # Mostrar vídeo se solicitado
                if show_video:
                    display_frame = frame.copy()
                    self.mp_drawing.draw_landmarks(display_frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                    
                    # Adicionar informações
                    status = "FALSO POSITIVO!" if fall_confirmed else "Possível FP..." if time_fallen_start else "ADL Normal"
                    color = (0,0,255) if fall_confirmed else (0,255,255) if time_fallen_start else (0,255,0)
                    cv2.putText(display_frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    cv2.putText(display_frame, f"ADL Frame: {frame_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
                    
                    cv2.imshow("ADL Fall Detection Test", display_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        
        cap.release()
        if show_video:
            cv2.destroyAllWindows()
        
        analysis_duration = time.time() - analysis_start_time
        detection_time = fall_detection_frame / fps if fall_detection_frame and fps > 0 else None
        
        # Para ADL: fall_detected=True significa FALSO POSITIVO
        is_false_positive = fall_confirmed
        
        return {
            'video': video_name,
            'video_type': 'ADL',
            'fall_detected': fall_confirmed,  # True = Falso Positivo
            'false_positive': is_false_positive,
            'detection_time': detection_time,
            'detection_frame': fall_detection_frame,
            'total_frames': total_frames,
            'video_duration': duration,
            'analysis_duration': analysis_duration,
            'fps': fps
        }
    
    def test_all_adl_videos(self, video_folder="data_set_videos_ADL", show_videos=False):
        """
        Testa todos os vídeos ADL na pasta especificada
        """
        print("=== TESTE DE FALSOS POSITIVOS - VÍDEOS ADL ===")
        print(f"Pasta de vídeos ADL: {video_folder}")
        print("IMPORTANTE: Vídeos ADL NÃO devem ser detectados como quedas")
        print("=" * 60)
        
        # Buscar todos os vídeos ADL
        video_pattern = os.path.join(video_folder, "*.mp4")
        video_files = sorted(glob.glob(video_pattern))
        
        if not video_files:
            print("Nenhum vídeo ADL encontrado!")
            return []
        
        print(f"Encontrados {len(video_files)} vídeos ADL")
        print("-" * 60)
        
        results = []
        false_positives = 0
        
        for i, video_path in enumerate(video_files, 1):
            print(f"\n[{i}/{len(video_files)}] ", end="")
            
            try:
                result = self.analyze_adl_video(video_path, show_video=show_videos)
                results.append(result)
                
                if result['false_positive']:
                    false_positives += 1
                    print(f"  ❌ FALSO POSITIVO detectado em {result['detection_time']:.1f}s")
                else:
                    print(f"  ✅ ADL Normal - Nenhuma queda detectada")
                    
            except Exception as e:
                print(f"  ❌ ERRO: {str(e)}")
                results.append({
                    'video': os.path.basename(video_path),
                    'video_type': 'ADL',
                    'fall_detected': False,
                    'false_positive': False,
                    'error': str(e),
                    'detection_time': None,
                    'detection_frame': None,
                    'total_frames': 0,
                    'video_duration': 0,
                    'analysis_duration': 0,
                    'fps': 0
                })
        
        print("\n" + "=" * 60)
        print(f"RESUMO ADL: {false_positives}/{len(video_files)} falsos positivos ({(false_positives/len(video_files)*100):.1f}%)")
        print(f"ESPECIFICIDADE: {((len(video_files)-false_positives)/len(video_files)*100):.1f}% (quanto maior, melhor)")
        
        return results
    
    def save_adl_results_to_csv(self, results, filename=None):
        """
        Salva os resultados ADL em um arquivo CSV
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"adl_false_positive_results_{timestamp}.csv"
        
        fieldnames = [
            'video', 'video_type', 'fall_detected', 'false_positive', 'detection_time', 
            'detection_frame', 'total_frames', 'video_duration', 'analysis_duration', 'fps', 'error'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                # Preencher campos faltantes
                row = {}
                for field in fieldnames:
                    row[field] = result.get(field, '')
                writer.writerow(row)
        
        print(f"\nResultados ADL salvos em: {filename}")
        return filename

def main():
    """
    Função principal para execução do teste ADL
    """
    tester = ADLFallDetectionTester()
    
    # Configurações
    SHOW_VIDEOS = False  # Mudar para True se quiser ver os vídeos durante o processamento
    ADL_VIDEO_FOLDER = "data_set_videos_ADL"
    
    # Executar teste em todos os vídeos ADL
    results = tester.test_all_adl_videos(ADL_VIDEO_FOLDER, show_videos=SHOW_VIDEOS)
    
    # Salvar resultados em CSV
    if results:
        csv_filename = tester.save_adl_results_to_csv(results)
        
        # Mostrar estatísticas detalhadas
        print(f"\n📊 ESTATÍSTICAS DETALHADAS - TESTE ADL:")
        print(f"📁 Total de vídeos ADL processados: {len(results)}")
        
        false_positives = [r for r in results if r['false_positive']]
        true_negatives = [r for r in results if not r['false_positive'] and not r.get('error')]
        error_cases = [r for r in results if r.get('error')]
        
        print(f"❌ Falsos Positivos (RUIM): {len(false_positives)}")
        print(f"✅ Verdadeiros Negativos (BOM): {len(true_negatives)}")
        print(f"⚠️  Erros de processamento: {len(error_cases)}")
        
        # Calcular métricas importantes
        total_valid = len(results) - len(error_cases)
        if total_valid > 0:
            specificity = (len(true_negatives) / total_valid) * 100
            false_positive_rate = (len(false_positives) / total_valid) * 100
            
            print(f"\n📈 MÉTRICAS DE QUALIDADE:")
            print(f"🎯 Especificidade: {specificity:.1f}% (meta: >95%)")
            print(f"⚠️  Taxa de Falsos Positivos: {false_positive_rate:.1f}% (meta: <5%)")
            
            if specificity >= 95:
                print("✅ EXCELENTE: Baixa taxa de falsos positivos!")
            elif specificity >= 90:
                print("✅ BOM: Taxa aceitável de falsos positivos")
            elif specificity >= 80:
                print("⚠️  MODERADO: Considere ajustar parâmetros")
            else:
                print("❌ RUIM: Muitos falsos positivos - ajustes necessários")
        
        if false_positives:
            print(f"\n❌ VÍDEOS COM FALSOS POSITIVOS:")
            for fp in false_positives:
                print(f"   {fp['video']} - detectado em {fp['detection_time']:.1f}s")
        
        print(f"\n📄 Relatório completo salvo em: {csv_filename}")

if __name__ == "__main__":
    main()