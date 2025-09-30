"""
Analisador completo que combina resultados de testes de quedas reais e vídeos ADL
Calcula métricas de precisão, sensibilidade, especificidade e acurácia geral
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import glob
from datetime import datetime

class CompletePrecisionAnalyzer:
    """
    Analisador completo de precisão do sistema de detecção de quedas
    """
    
    def __init__(self):
        self.fall_results = None
        self.adl_results = None
        self.combined_results = None
    
    def load_results(self):
        """
        Carrega os resultados mais recentes de ambos os tipos de teste
        """
        print("📁 Carregando arquivos de resultados...")
        
        # Carregar resultados de quedas reais (buscar no diretório pai)
        fall_files = glob.glob("../fall_detection_results_*.csv")
        if not fall_files:
            fall_files = glob.glob("../teste_rapido_resultados.csv")
        if not fall_files:
            # Tentar no diretório atual também
            fall_files = glob.glob("fall_detection_results_*.csv")
        if not fall_files:
            fall_files = glob.glob("teste_rapido_resultados.csv")
        
        if fall_files:
            latest_fall_file = max(fall_files, key=os.path.getctime)
            print(f"  ✅ Quedas reais: {latest_fall_file}")
            self.fall_results = pd.read_csv(latest_fall_file)
            self.fall_results['expected_result'] = True  # Esperamos detectar quedas
        else:
            print("  ❌ Nenhum arquivo de resultados de quedas encontrado!")
            return False
        
        # Carregar resultados de ADL (buscar no diretório atual)
        adl_files = glob.glob("adl_false_positive_results_*.csv")
        if not adl_files:
            adl_files = glob.glob("teste_rapido_adl_resultados.csv")
        
        if adl_files:
            latest_adl_file = max(adl_files, key=os.path.getctime)
            print(f"  ✅ Vídeos ADL: {latest_adl_file}")
            self.adl_results = pd.read_csv(latest_adl_file)
            self.adl_results['expected_result'] = False  # NÃO esperamos detectar quedas
        else:
            print("  ⚠️ Nenhum arquivo de resultados ADL encontrado - usando apenas quedas reais")
            self.adl_results = pd.DataFrame()
        
        return True
    
    def calculate_metrics(self):
        """
        Calcula métricas de performance do sistema
        """
        if self.fall_results is None:
            return None
        
        # Combinar resultados
        if not self.adl_results.empty:
            self.combined_results = pd.concat([self.fall_results, self.adl_results], ignore_index=True)
        else:
            self.combined_results = self.fall_results.copy()
        
        # Remover linhas com erro
        valid_results = self.combined_results[
            (self.combined_results['error'].isna()) | (self.combined_results['error'] == '')
        ].copy()
        
        if len(valid_results) == 0:
            return None
        
        # Calcular métricas de classificação
        tp = len(valid_results[(valid_results['expected_result'] == True) & (valid_results['fall_detected'] == True)])   # Verdadeiro Positivo
        tn = len(valid_results[(valid_results['expected_result'] == False) & (valid_results['fall_detected'] == False)]) # Verdadeiro Negativo
        fp = len(valid_results[(valid_results['expected_result'] == False) & (valid_results['fall_detected'] == True)])  # Falso Positivo
        fn = len(valid_results[(valid_results['expected_result'] == True) & (valid_results['fall_detected'] == False)])  # Falso Negativo
        
        # Métricas derivadas
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0  # Sensibilidade/Recall
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # Especificidade
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0    # Precisão
        accuracy = (tp + tn) / (tp + tn + fp + fn)            # Acurácia
        f1_score = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
        
        metrics = {
            'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
            'sensitivity': sensitivity * 100,
            'specificity': specificity * 100,
            'precision': precision * 100,
            'accuracy': accuracy * 100,
            'f1_score': f1_score * 100,
            'total_videos': len(valid_results),
            'fall_videos': len(valid_results[valid_results['expected_result'] == True]),
            'adl_videos': len(valid_results[valid_results['expected_result'] == False])
        }
        
        return metrics, valid_results
    
    def print_detailed_analysis(self, metrics, results):
        """
        Imprime análise detalhada dos resultados
        """
        print("\n" + "=" * 70)
        print("📊 ANÁLISE COMPLETA DE PRECISÃO DO SISTEMA")
        print("=" * 70)
        
        print(f"📁 DADOS ANALISADOS:")
        print(f"   Total de vídeos: {metrics['total_videos']}")
        print(f"   Vídeos de quedas reais: {metrics['fall_videos']}")
        print(f"   Vídeos ADL (atividades normais): {metrics['adl_videos']}")
        
        print(f"\n📈 MATRIZ DE CONFUSÃO:")
        print(f"   Verdadeiros Positivos (TP): {metrics['tp']} - Quedas detectadas corretamente")
        print(f"   Verdadeiros Negativos (TN): {metrics['tn']} - ADL não detectadas como quedas")
        print(f"   Falsos Positivos (FP): {metrics['fp']} - ADL detectadas como quedas (RUIM)")
        print(f"   Falsos Negativos (FN): {metrics['fn']} - Quedas não detectadas (RUIM)")
        
        print(f"\n🎯 MÉTRICAS DE PERFORMANCE:")
        print(f"   Sensibilidade (Recall): {metrics['sensitivity']:.1f}% - Capacidade de detectar quedas reais")
        print(f"   Especificidade: {metrics['specificity']:.1f}% - Capacidade de NÃO detectar em atividades normais")
        print(f"   Precisão: {metrics['precision']:.1f}% - Das detecções, quantas são realmente quedas")
        print(f"   Acurácia Geral: {metrics['accuracy']:.1f}% - Porcentagem geral de acertos")
        print(f"   F1-Score: {metrics['f1_score']:.1f}% - Média harmônica entre precisão e sensibilidade")
        
        print(f"\n📋 INTERPRETAÇÃO DOS RESULTADOS:")
        
        # Análise da Sensibilidade
        if metrics['sensitivity'] >= 90:
            print(f"   ✅ SENSIBILIDADE EXCELENTE: Detecta {metrics['sensitivity']:.1f}% das quedas reais")
        elif metrics['sensitivity'] >= 80:
            print(f"   ✅ SENSIBILIDADE BOA: Detecta {metrics['sensitivity']:.1f}% das quedas reais")
        elif metrics['sensitivity'] >= 70:
            print(f"   ⚠️  SENSIBILIDADE MODERADA: Detecta apenas {metrics['sensitivity']:.1f}% das quedas reais")
        else:
            print(f"   ❌ SENSIBILIDADE BAIXA: Detecta apenas {metrics['sensitivity']:.1f}% das quedas reais")
        
        # Análise da Especificidade
        if metrics['specificity'] >= 95:
            print(f"   ✅ ESPECIFICIDADE EXCELENTE: {metrics['fp']} falsos positivos em {metrics['adl_videos']} vídeos ADL")
        elif metrics['specificity'] >= 90:
            print(f"   ✅ ESPECIFICIDADE BOA: {metrics['fp']} falsos positivos em {metrics['adl_videos']} vídeos ADL")
        elif metrics['specificity'] >= 80:
            print(f"   ⚠️  ESPECIFICIDADE MODERADA: {metrics['fp']} falsos positivos em {metrics['adl_videos']} vídeos ADL")
        else:
            print(f"   ❌ ESPECIFICIDADE BAIXA: {metrics['fp']} falsos positivos em {metrics['adl_videos']} vídeos ADL")
        
        # Análise Geral
        if metrics['accuracy'] >= 90:
            print(f"   🎯 SISTEMA EXCELENTE: {metrics['accuracy']:.1f}% de acurácia geral")
        elif metrics['accuracy'] >= 80:
            print(f"   🎯 SISTEMA BOM: {metrics['accuracy']:.1f}% de acurácia geral")
        elif metrics['accuracy'] >= 70:
            print(f"   🎯 SISTEMA MODERADO: {metrics['accuracy']:.1f}% de acurácia geral")
        else:
            print(f"   🎯 SISTEMA PRECISA MELHORIAS: {metrics['accuracy']:.1f}% de acurácia geral")
        
        # Casos problemáticos
        fall_not_detected = results[(results['expected_result'] == True) & (results['fall_detected'] == False)]
        adl_false_positive = results[(results['expected_result'] == False) & (results['fall_detected'] == True)]
        
        if len(fall_not_detected) > 0:
            print(f"\n❌ QUEDAS NÃO DETECTADAS ({len(fall_not_detected)}):")
            for _, row in fall_not_detected.iterrows():
                print(f"   {row['video']}")
        
        if len(adl_false_positive) > 0:
            print(f"\n❌ FALSOS POSITIVOS EM ADL ({len(adl_false_positive)}):")
            for _, row in adl_false_positive.iterrows():
                detection_info = f" (detectado em {row['detection_time']:.1f}s)" if pd.notna(row['detection_time']) else ""
                print(f"   {row['video']}{detection_info}")
    
    def create_comprehensive_visualizations(self, metrics, results):
        """
        Cria visualizações completas dos resultados
        """
        try:
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle('Análise Completa do Sistema de Detecção de Quedas', fontsize=16, fontweight='bold')
            
            # 1. Matriz de Confusão (formato correto)
            # Linha 1: Queda Real -> [FN, TP] 
            # Linha 2: ADL Normal -> [TN, FP]
            confusion_matrix = np.array([[metrics['fn'], metrics['tp']], 
                                       [metrics['tn'], metrics['fp']]])
            
            # Criar anotações personalizadas para a matriz
            annot_matrix = np.array([[f'{metrics["fn"]}\n(FN)', f'{metrics["tp"]}\n(TP)'], 
                                   [f'{metrics["tn"]}\n(TN)', f'{metrics["fp"]}\n(FP)']])
            
            sns.heatmap(confusion_matrix, annot=annot_matrix, fmt='', cmap='Blues', 
                       yticklabels=['Queda Real', 'ADL Normal'],
                       ax=axes[0,0])
            axes[0,0].set_title('Matriz de Confusão\n(TP=Verdadeiro+, TN=Verdadeiro-, FP=Falso+, FN=Falso-)')
            axes[0,0].set_xlabel('Predição do Sistema')
            axes[0,0].set_ylabel('Realidade')
            
            # 2. Métricas de Performance
            metrics_names = ['Sensibilidade', 'Especificidade', 'Precisão', 'Acurácia', 'F1-Score']
            metrics_values = [metrics['sensitivity'], metrics['specificity'], 
                            metrics['precision'], metrics['accuracy'], metrics['f1_score']]
            
            colors = ['green' if v >= 80 else 'orange' if v >= 70 else 'red' for v in metrics_values]
            bars = axes[0,1].bar(metrics_names, metrics_values, color=colors, alpha=0.7)
            axes[0,1].set_title('Métricas de Performance (%)')
            axes[0,1].set_ylim(0, 100)
            axes[0,1].tick_params(axis='x', rotation=45)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, metrics_values):
                axes[0,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                              f'{value:.1f}%', ha='center', va='bottom')
            
            # 3. Distribuição de Tipos de Vídeo
            video_types = ['Quedas Reais', 'Vídeos ADL']
            video_counts = [metrics['fall_videos'], metrics['adl_videos']]
            axes[0,2].pie(video_counts, labels=video_types, autopct='%1.1f%%', 
                         colors=['#ff7f7f', '#7f7fff'])
            axes[0,2].set_title('Distribuição dos Vídeos Testados')
            
            # 4. Resultados por Tipo de Vídeo
            fall_results = results[results['expected_result'] == True]
            adl_results = results[results['expected_result'] == False]
            
            if len(fall_results) > 0:
                fall_detected = len(fall_results[fall_results['fall_detected'] == True])
                fall_missed = len(fall_results[fall_results['fall_detected'] == False])
                
                axes[1,0].bar(['Detectadas', 'Perdidas'], [fall_detected, fall_missed], 
                             color=['green', 'red'], alpha=0.7)
                axes[1,0].set_title('Quedas Reais: Detecção')
                axes[1,0].set_ylabel('Número de Vídeos')
            
            # 5. Falsos Positivos em ADL
            if len(adl_results) > 0:
                adl_correct = len(adl_results[adl_results['fall_detected'] == False])
                adl_false_pos = len(adl_results[adl_results['fall_detected'] == True])
                
                axes[1,1].bar(['Corretos', 'Falsos Positivos'], [adl_correct, adl_false_pos], 
                             color=['green', 'red'], alpha=0.7)
                axes[1,1].set_title('Vídeos ADL: Especificidade')
                axes[1,1].set_ylabel('Número de Vídeos')
            
            # 6. Tempos de Detecção
            detected_results = results[results['fall_detected'] == True]
            if len(detected_results) > 0 and detected_results['detection_time'].notna().any():
                axes[1,2].hist(detected_results['detection_time'].dropna(), 
                              bins=10, color='skyblue', edgecolor='black', alpha=0.7)
                axes[1,2].set_title('Distribuição dos Tempos de Detecção')
                axes[1,2].set_xlabel('Tempo (segundos)')
                axes[1,2].set_ylabel('Número de Detecções')
            
            plt.tight_layout()
            
            # Salvar gráfico
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"analise_completa_precisao_{timestamp}.png"
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            print(f"\n📊 Gráficos salvos em: {chart_filename}")
            
            plt.show()
            
        except Exception as e:
            print(f"⚠️ Erro ao criar visualizações: {e}")
    
    def save_complete_report(self, metrics, results):
        """
        Salva relatório completo em arquivo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"relatorio_completo_precisao_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO COMPLETO DE PRECISÃO - SISTEMA DE DETECÇÃO DE QUEDAS\n")
            f.write("=" * 70 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            f.write("RESUMO EXECUTIVO:\n")
            f.write(f"Total de vídeos testados: {metrics['total_videos']}\n")
            f.write(f"Vídeos de quedas reais: {metrics['fall_videos']}\n")
            f.write(f"Vídeos ADL (atividades normais): {metrics['adl_videos']}\n")
            f.write(f"Acurácia geral: {metrics['accuracy']:.1f}%\n")
            f.write(f"Sensibilidade: {metrics['sensitivity']:.1f}%\n")
            f.write(f"Especificidade: {metrics['specificity']:.1f}%\n\n")
            
            f.write("MATRIZ DE CONFUSÃO:\n")
            f.write(f"Verdadeiros Positivos: {metrics['tp']}\n")
            f.write(f"Verdadeiros Negativos: {metrics['tn']}\n")
            f.write(f"Falsos Positivos: {metrics['fp']}\n")
            f.write(f"Falsos Negativos: {metrics['fn']}\n\n")
            
            f.write("DETALHES POR VÍDEO:\n")
            f.write("-" * 70 + "\n")
            
            for _, row in results.iterrows():
                expected = "QUEDA" if row['expected_result'] else "ADL"
                detected = "SIM" if row['fall_detected'] else "NÃO"
                
                if row['expected_result'] and row['fall_detected']:
                    result_type = "✅ TP"
                elif not row['expected_result'] and not row['fall_detected']:
                    result_type = "✅ TN"
                elif not row['expected_result'] and row['fall_detected']:
                    result_type = "❌ FP"
                else:
                    result_type = "❌ FN"
                
                detection_info = f" (em {row['detection_time']:.1f}s)" if row['fall_detected'] and pd.notna(row['detection_time']) else ""
                
                f.write(f"{row['video']}: {expected} | Detectado: {detected}{detection_info} | {result_type}\n")
        
        print(f"📄 Relatório completo salvo em: {report_filename}")
        return report_filename

def main():
    """
    Função principal para análise completa
    """
    print("=== ANÁLISE COMPLETA DE PRECISÃO DO SISTEMA ===")
    
    analyzer = CompletePrecisionAnalyzer()
    
    # Carregar resultados
    if not analyzer.load_results():
        print("❌ Não foi possível carregar os resultados necessários!")
        print("   Execute primeiro os testes de quedas e ADL:")
        print("   1. python automated_fall_detection_test.py")
        print("   2. python data_set_ADL_codes/adl_test_automated.py")
        return
    
    # Calcular métricas
    result = analyzer.calculate_metrics()
    if result is None:
        print("❌ Não foi possível calcular as métricas!")
        return
    
    metrics, results = result
    
    # Análise detalhada
    analyzer.print_detailed_analysis(metrics, results)
    
    # Visualizações
    print(f"\n📊 Criando visualizações completas...")
    analyzer.create_comprehensive_visualizations(metrics, results)
    
    # Salvar relatório
    analyzer.save_complete_report(metrics, results)
    
    print(f"\n🎯 CONCLUSÃO:")
    if metrics['accuracy'] >= 85 and metrics['sensitivity'] >= 80 and metrics['specificity'] >= 90:
        print("   ✅ Sistema com performance EXCELENTE para detecção de quedas!")
    elif metrics['accuracy'] >= 75:
        print("   ✅ Sistema com performance BOA - pequenos ajustes podem melhorar")
    else:
        print("   ⚠️ Sistema precisa de ajustes nos parâmetros de detecção")

if __name__ == "__main__":
    main()