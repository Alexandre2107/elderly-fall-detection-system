"""
Script simples para testar alguns vídeos específicos
Útil para validação rápida antes de processar todos os 30 vídeos
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from data_set_codes.automated_fall_detection_test import FallDetectionTester

def test_specific_videos():
    """
    Testa alguns vídeos específicos para validação
    """
    tester = FallDetectionTester()
    
    # Lista de vídeos para teste rápido
    test_videos = [
        "data_set_videos/fall-01-cam0.mp4",
        "data_set_videos/fall-02-cam0.mp4", 
        "data_set_videos/fall-03-cam0.mp4",
        "data_set_videos/fall-05-cam0.mp4",
        "data_set_videos/fall-10-cam0.mp4"
    ]
    
    print("=== TESTE RÁPIDO - 5 VÍDEOS ===")
    
    results = []
    
    for i, video_path in enumerate(test_videos, 1):
        if os.path.exists(video_path):
            print(f"\n[{i}/5] Testando: {os.path.basename(video_path)}")
            
            try:
                result = tester.analyze_video(video_path, show_video=False)
                results.append(result)
                
                if result['fall_detected']:
                    print(f"  ✅ QUEDA DETECTADA em {result['detection_time']:.1f}s")
                else:
                    print(f"  ❌ Nenhuma queda detectada")
                    
            except Exception as e:
                print(f"  ❌ ERRO: {str(e)}")
        else:
            print(f"\n[{i}/5] ❌ Vídeo não encontrado: {video_path}")
    
    if results:
        # Salvar resultados do teste rápido
        filename = tester.save_results_to_csv(results, "teste_rapido_resultados.csv")
        
        detections = sum(1 for r in results if r['fall_detected'])
        print(f"\n📊 RESULTADO DO TESTE RÁPIDO:")
        print(f"   Vídeos testados: {len(results)}")
        print(f"   Quedas detectadas: {detections}/{len(results)} ({detections/len(results)*100:.1f}%)")
        print(f"   Arquivo salvo: {filename}")

if __name__ == "__main__":
    test_specific_videos()