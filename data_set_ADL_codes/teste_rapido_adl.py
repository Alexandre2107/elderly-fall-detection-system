"""
Script para teste rápido de vídeos ADL (Activities of Daily Living)
Testa apenas alguns vídeos ADL para validação rápida
"""

import sys
import os

# Adicionar o diretório pai ao path para importar o módulo
parent_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(parent_dir)

from data_set_ADL_codes.adl_test_automated import ADLFallDetectionTester

def test_specific_adl_videos():
    """
    Testa alguns vídeos ADL específicos para validação rápida
    """
    tester = ADLFallDetectionTester()
    
    # Lista de vídeos ADL para teste rápido
    test_videos = [
        "data_set_videos_ADL/adl-01-cam0.mp4",
        "data_set_videos_ADL/adl-05-cam0.mp4", 
        "data_set_videos_ADL/adl-10-cam0.mp4",
        "data_set_videos_ADL/adl-15-cam0.mp4",
        "data_set_videos_ADL/adl-20-cam0.mp4",
        "data_set_videos_ADL/adl-25-cam0.mp4",
        "data_set_videos_ADL/adl-30-cam0.mp4",
        "data_set_videos_ADL/adl-35-cam0.mp4"
    ]
    
    print("=== TESTE RÁPIDO ADL - 8 VÍDEOS ===")
    print("OBJETIVO: Verificar falsos positivos em atividades normais")
    print("EXPECTATIVA: 0% de detecção de quedas (100% especificidade)")
    print("=" * 50)
    
    results = []
    false_positives = 0
    
    for i, video_path in enumerate(test_videos, 1):
        if os.path.exists(video_path):
            print(f"\n[{i}/8] Testando ADL: {os.path.basename(video_path)}")
            
            try:
                result = tester.analyze_adl_video(video_path, show_video=False)
                results.append(result)
                
                if result['false_positive']:
                    false_positives += 1
                    print(f"  ❌ FALSO POSITIVO em {result['detection_time']:.1f}s")
                else:
                    print(f"  ✅ Normal - Nenhuma queda detectada")
                    
            except Exception as e:
                print(f"  ❌ ERRO: {str(e)}")
        else:
            print(f"\n[{i}/8] ❌ Vídeo ADL não encontrado: {video_path}")
    
    if results:
        # Salvar resultados do teste rápido
        filename = tester.save_adl_results_to_csv(results, "teste_rapido_adl_resultados.csv")
        
        true_negatives = len(results) - false_positives
        specificity = (true_negatives / len(results)) * 100 if results else 0
        
        print(f"\n📊 RESULTADO DO TESTE RÁPIDO ADL:")
        print(f"   Vídeos ADL testados: {len(results)}")
        print(f"   Falsos Positivos: {false_positives}/{len(results)} ({(false_positives/len(results)*100):.1f}%)")
        print(f"   Especificidade: {specificity:.1f}% (meta: >95%)")
        
        if specificity >= 95:
            print("   ✅ RESULTADO: Excelente especificidade!")
        elif specificity >= 90:
            print("   ✅ RESULTADO: Boa especificidade")
        elif specificity >= 80:
            print("   ⚠️  RESULTADO: Especificidade moderada")
        else:
            print("   ❌ RESULTADO: Baixa especificidade - muitos falsos positivos")
        
        print(f"   📄 Arquivo salvo: {filename}")
        
        # Interpretação dos resultados
        print(f"\n💡 INTERPRETAÇÃO:")
        print(f"   • Especificidade: Capacidade de NÃO detectar quedas em atividades normais")
        print(f"   • Falso Positivo: Sistema detecta queda quando não há queda")
        print(f"   • Meta ideal: 0% falsos positivos (100% especificidade)")

if __name__ == "__main__":
    test_specific_adl_videos()