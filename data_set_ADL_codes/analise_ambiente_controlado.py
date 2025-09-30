"""
Analisador de precisão para ambiente controlado com dados específicos
Gera visualizações e relatórios com métricas pré-definidas
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime

class ControlledEnvironmentAnalyzer:
    """
    Analisador para resultados em ambiente controlado
    """
    
    def __init__(self):
        # Dados do ambiente controlado
        self.metrics = {
            'total_videos': 70,
            'fall_videos': 30,
            'adl_videos': 40,
            'tp': 28,  # Verdadeiros Positivos
            'tn': 40,  # Verdadeiros Negativos  
            'fp': 0,   # Falsos Positivos
            'fn': 2,   # Falsos Negativos
        }
        
        # Calcular métricas derivadas
        self.calculate_derived_metrics()
    
    def calculate_derived_metrics(self):
        """
        Calcula métricas derivadas a partir dos dados base
        """
        tp, tn, fp, fn = self.metrics['tp'], self.metrics['tn'], self.metrics['fp'], self.metrics['fn']
        
        # Métricas de performance
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0  # Sensibilidade/Recall
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0  # Especificidade
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0    # Precisão
        accuracy = (tp + tn) / (tp + tn + fp + fn)            # Acurácia
        f1_score = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0
        
        # Adicionar métricas calculadas
        self.metrics.update({
            'sensitivity': sensitivity * 100,
            'specificity': specificity * 100,
            'precision': precision * 100,
            'accuracy': accuracy * 100,
            'f1_score': f1_score * 100
        })
    
    def print_detailed_analysis(self):
        """
        Imprime análise detalhada dos resultados
        """
        print("\n" + "=" * 80)
        print("📊 ANÁLISE COMPLETA DO SISTEMA DE DETECÇÃO DE QUEDAS EM AMBIENTE CONTROLADO")
        print("=" * 80)
        
        print(f"📁 DADOS DO AMBIENTE CONTROLADO:")
        print(f"   Total de vídeos testados: {self.metrics['total_videos']}")
        print(f"   Vídeos de quedas reais: {self.metrics['fall_videos']}")
        print(f"   Vídeos de atividades normais (ADL): {self.metrics['adl_videos']}")
        
        print(f"\n📈 MATRIZ DE CONFUSÃO:")
        print(f"   Verdadeiros Positivos (TP): {self.metrics['tp']} - Quedas detectadas corretamente")
        print(f"   Verdadeiros Negativos (TN): {self.metrics['tn']} - ADL não detectadas como quedas")
        print(f"   Falsos Positivos (FP): {self.metrics['fp']} - ADL detectadas como quedas (RUIM)")
        print(f"   Falsos Negativos (FN): {self.metrics['fn']} - Quedas não detectadas (RUIM)")
        
        print(f"\n🎯 MÉTRICAS DE PERFORMANCE:")
        print(f"   Sensibilidade (Recall): {self.metrics['sensitivity']:.1f}% - Capacidade de detectar quedas reais")
        print(f"   Especificidade: {self.metrics['specificity']:.1f}% - Capacidade de NÃO detectar em atividades normais")
        print(f"   Precisão: {self.metrics['precision']:.1f}% - Das detecções, quantas são realmente quedas")
        print(f"   Acurácia Geral: {self.metrics['accuracy']:.1f}% - Porcentagem geral de acertos")
        print(f"   F1-Score: {self.metrics['f1_score']:.1f}% - Média harmônica entre precisão e sensibilidade")
        
        print(f"\n📋 INTERPRETAÇÃO DOS RESULTADOS:")
        
        # Análise da Sensibilidade
        if self.metrics['sensitivity'] >= 90:
            print(f"   ✅ SENSIBILIDADE EXCELENTE: Detecta {self.metrics['sensitivity']:.1f}% das quedas reais")
        elif self.metrics['sensitivity'] >= 80:
            print(f"   ✅ SENSIBILIDADE BOA: Detecta {self.metrics['sensitivity']:.1f}% das quedas reais")
        elif self.metrics['sensitivity'] >= 70:
            print(f"   ⚠️  SENSIBILIDADE MODERADA: Detecta apenas {self.metrics['sensitivity']:.1f}% das quedas reais")
        else:
            print(f"   ❌ SENSIBILIDADE BAIXA: Detecta apenas {self.metrics['sensitivity']:.1f}% das quedas reais")
        
        # Análise da Especificidade
        if self.metrics['specificity'] >= 95:
            print(f"   ✅ ESPECIFICIDADE EXCELENTE: {self.metrics['fp']} falsos positivos em {self.metrics['adl_videos']} vídeos ADL")
        elif self.metrics['specificity'] >= 90:
            print(f"   ✅ ESPECIFICIDADE BOA: {self.metrics['fp']} falsos positivos em {self.metrics['adl_videos']} vídeos ADL")
        elif self.metrics['specificity'] >= 80:
            print(f"   ⚠️  ESPECIFICIDADE MODERADA: {self.metrics['fp']} falsos positivos em {self.metrics['adl_videos']} vídeos ADL")
        else:
            print(f"   ❌ ESPECIFICIDADE BAIXA: {self.metrics['fp']} falsos positivos em {self.metrics['adl_videos']} vídeos ADL")
        
        # Análise Geral
        if self.metrics['accuracy'] >= 90:
            print(f"   🎯 SISTEMA EXCELENTE: {self.metrics['accuracy']:.1f}% de acurácia geral")
        elif self.metrics['accuracy'] >= 80:
            print(f"   🎯 SISTEMA BOM: {self.metrics['accuracy']:.1f}% de acurácia geral")
        elif self.metrics['accuracy'] >= 70:
            print(f"   🎯 SISTEMA MODERADO: {self.metrics['accuracy']:.1f}% de acurácia geral")
        else:
            print(f"   🎯 SISTEMA PRECISA MELHORIAS: {self.metrics['accuracy']:.1f}% de acurácia geral")
        
        # Análise específica dos resultados
        if self.metrics['fn'] > 0:
            print(f"\n❌ QUEDAS NÃO DETECTADAS: {self.metrics['fn']} vídeos")
            print(f"   - Representam {(self.metrics['fn']/self.metrics['fall_videos']*100):.1f}% das quedas reais")
        
        if self.metrics['fp'] == 0:
            print(f"\n✅ EXCELENTE: Nenhum falso positivo detectado!")
            print(f"   - 100% de especificidade em atividades normais")
        elif self.metrics['fp'] > 0:
            print(f"\n⚠️ FALSOS POSITIVOS: {self.metrics['fp']} em {self.metrics['adl_videos']} vídeos ADL")
    
    def create_comprehensive_visualizations(self):
        """
        Cria visualizações completas dos resultados
        """
        try:
            plt.style.use('default')
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            fig.suptitle('Análise Completa do Sistema de Detecção de Quedas em Ambiente Controlado', 
                        fontsize=16, fontweight='bold')
            
            # 1. Matriz de Confusão
            confusion_matrix = np.array([[self.metrics['fn'], self.metrics['tp']], 
                                       [self.metrics['tn'], self.metrics['fp']]])
            
            # Criar anotações personalizadas para a matriz
            annot_matrix = np.array([[f'{self.metrics["fn"]}\n(FN)', f'{self.metrics["tp"]}\n(TP)'], 
                                   [f'{self.metrics["tn"]}\n(TN)', f'{self.metrics["fp"]}\n(FP)']])
            
            sns.heatmap(confusion_matrix, annot=annot_matrix, fmt='', cmap='Blues', 
                       xticklabels=['Não Detectado', 'Detectado'],
                       yticklabels=['Queda Real', 'ADL Normal'],
                       ax=axes[0,0], cbar_kws={'shrink': 0.8})
            axes[0,0].set_title('Matriz de Confusão\n(TP=Verdadeiro+, TN=Verdadeiro-, FP=Falso+, FN=Falso-)')
            axes[0,0].set_xlabel('Predição do Sistema')
            axes[0,0].set_ylabel('Realidade')
            
            # 2. Métricas de Performance
            metrics_names = ['Sensibilidade', 'Especificidade', 'Precisão', 'Acurácia', 'F1-Score']
            metrics_values = [self.metrics['sensitivity'], self.metrics['specificity'], 
                            self.metrics['precision'], self.metrics['accuracy'], self.metrics['f1_score']]
            
            colors = ['green' if v >= 80 else 'orange' if v >= 70 else 'red' for v in metrics_values]
            bars = axes[0,1].bar(metrics_names, metrics_values, color=colors, alpha=0.7)
            axes[0,1].set_title('Métricas de Performance (%)')
            axes[0,1].set_ylim(0, 105)
            axes[0,1].tick_params(axis='x', rotation=45)
            axes[0,1].grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, metrics_values):
                axes[0,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                              f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # 3. Distribuição de Tipos de Vídeo
            video_types = ['Quedas Reais', 'Atividades Normais']
            video_counts = [self.metrics['fall_videos'], self.metrics['adl_videos']]
            colors_pie = ['#ff7f7f', '#7f7fff']
            
            wedges, texts, autotexts = axes[0,2].pie(video_counts, labels=video_types, autopct='%1.1f%%', 
                                                   colors=colors_pie, startangle=90)
            axes[0,2].set_title('Distribuição dos Vídeos Testados')
            
            # Melhorar legibilidade do gráfico de pizza
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # 4. Resultados das Quedas Reais
            fall_detected = self.metrics['tp']
            fall_missed = self.metrics['fn']
            
            bars_fall = axes[1,0].bar(['Detectadas', 'Perdidas'], [fall_detected, fall_missed], 
                         color=['green', 'red'], alpha=0.7)
            axes[1,0].set_title(f'Quedas Reais: Detecção\n(Total: {self.metrics["fall_videos"]} vídeos)')
            axes[1,0].set_ylabel('Número de Vídeos')
            axes[1,0].grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bar in bars_fall:
                height = bar.get_height()
                axes[1,0].text(bar.get_x() + bar.get_width()/2, height + 0.5,
                              f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            # 5. Especificidade em ADL
            adl_correct = self.metrics['tn']
            adl_false_pos = self.metrics['fp']
            
            bars_adl = axes[1,1].bar(['Corretos', 'Falsos Positivos'], [adl_correct, adl_false_pos], 
                         color=['green', 'red'], alpha=0.7)
            axes[1,1].set_title(f'Atividades Normais: Especificidade\n(Total: {self.metrics["adl_videos"]} vídeos)')
            axes[1,1].set_ylabel('Número de Vídeos')
            axes[1,1].grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bar in bars_adl:
                height = bar.get_height()
                axes[1,1].text(bar.get_x() + bar.get_width()/2, height + 0.5,
                              f'{int(height)}', ha='center', va='bottom', fontweight='bold')
            
            # 6. Resumo das Métricas Principais
            main_metrics = ['Acurácia', 'Sensibilidade', 'Especificidade']
            main_values = [self.metrics['accuracy'], self.metrics['sensitivity'], self.metrics['specificity']]
            colors_main = ['blue', 'green', 'orange']
            
            bars_main = axes[1,2].bar(main_metrics, main_values, color=colors_main, alpha=0.7)
            axes[1,2].set_title('Métricas Principais (%)')
            axes[1,2].set_ylim(0, 105)
            axes[1,2].set_ylabel('Porcentagem (%)')
            axes[1,2].grid(True, alpha=0.3)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars_main, main_values):
                axes[1,2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                              f'{value:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            # Adicionar linha de referência em 80% e 95%
            axes[1,2].axhline(y=80, color='red', linestyle='--', alpha=0.7, label='Meta Mínima (80%)')
            axes[1,2].axhline(y=95, color='green', linestyle='--', alpha=0.7, label='Meta Excelente (95%)')
            axes[1,2].legend()
            
            plt.tight_layout()
            
            # Salvar gráfico
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            chart_filename = f"analise_completa_ambiente_controlado_{timestamp}.png"
            plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
            print(f"\n📊 Gráficos salvos em: {chart_filename}")
            
            plt.show()
            
        except Exception as e:
            print(f"⚠️ Erro ao criar visualizações: {e}")
            print("   Certifique-se de ter matplotlib e seaborn instalados")
    
    def save_complete_report(self):
        """
        Salva relatório completo em arquivo
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"relatorio_ambiente_controlado_{timestamp}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("ANÁLISE COMPLETA DO SISTEMA DE DETECÇÃO DE QUEDAS EM AMBIENTE CONTROLADO\n")
            f.write("=" * 80 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            
            f.write("RESUMO EXECUTIVO:\n")
            f.write(f"Total de vídeos testados: {self.metrics['total_videos']}\n")
            f.write(f"Vídeos de quedas reais: {self.metrics['fall_videos']}\n")
            f.write(f"Vídeos de atividades normais (ADL): {self.metrics['adl_videos']}\n")
            f.write(f"Acurácia geral: {self.metrics['accuracy']:.1f}%\n")
            f.write(f"Sensibilidade: {self.metrics['sensitivity']:.1f}%\n")
            f.write(f"Especificidade: {self.metrics['specificity']:.1f}%\n\n")
            
            f.write("MATRIZ DE CONFUSÃO:\n")
            f.write(f"Verdadeiros Positivos (TP): {self.metrics['tp']}\n")
            f.write(f"Verdadeiros Negativos (TN): {self.metrics['tn']}\n")
            f.write(f"Falsos Positivos (FP): {self.metrics['fp']}\n")
            f.write(f"Falsos Negativos (FN): {self.metrics['fn']}\n\n")
            
            f.write("ANÁLISE DETALHADA:\n")
            f.write(f"Taxa de Detecção de Quedas: {(self.metrics['tp']/self.metrics['fall_videos']*100):.1f}%\n")
            f.write(f"Taxa de Falsos Positivos: {(self.metrics['fp']/self.metrics['adl_videos']*100):.1f}%\n")
            f.write(f"Taxa de Falsos Negativos: {(self.metrics['fn']/self.metrics['fall_videos']*100):.1f}%\n\n")
            
            f.write("CONCLUSÕES:\n")
            if self.metrics['accuracy'] >= 90:
                f.write("✅ Sistema apresenta EXCELENTE performance em ambiente controlado\n")
            elif self.metrics['accuracy'] >= 80:
                f.write("✅ Sistema apresenta BOA performance em ambiente controlado\n")
            else:
                f.write("⚠️ Sistema precisa de ajustes para melhorar performance\n")
                
            if self.metrics['fp'] == 0:
                f.write("✅ Ausência total de falsos positivos - excelente especificidade\n")
            
            if self.metrics['sensitivity'] >= 90:
                f.write("✅ Excelente capacidade de detectar quedas reais\n")
            elif self.metrics['sensitivity'] >= 80:
                f.write("✅ Boa capacidade de detectar quedas reais\n")
            else:
                f.write("⚠️ Capacidade moderada de detectar quedas - considerar ajustes\n")
        
        print(f"📄 Relatório completo salvo em: {report_filename}")
        return report_filename

def main():
    """
    Função principal para análise do ambiente controlado
    """
    print("=== ANÁLISE DO SISTEMA EM AMBIENTE CONTROLADO ===")
    
    analyzer = ControlledEnvironmentAnalyzer()
    
    # Análise detalhada
    analyzer.print_detailed_analysis()
    
    # Visualizações
    print(f"\n📊 Criando visualizações do ambiente controlado...")
    analyzer.create_comprehensive_visualizations()
    
    # Salvar relatório
    analyzer.save_complete_report()
    
    print(f"\n🎯 CONCLUSÃO GERAL:")
    if analyzer.metrics['accuracy'] >= 90 and analyzer.metrics['sensitivity'] >= 85 and analyzer.metrics['specificity'] >= 95:
        print("   ✅ Sistema com performance EXCELENTE em ambiente controlado!")
        print("   🚀 Pronto para implementação em cenários reais")
    elif analyzer.metrics['accuracy'] >= 80:
        print("   ✅ Sistema com performance BOA - adequado para uso prático")
        print("   🔧 Pequenos ajustes podem otimizar ainda mais a performance")
    else:
        print("   ⚠️ Sistema precisa de ajustes antes da implementação")
        
    print(f"\n📈 DESTAQUES:")
    print(f"   • {analyzer.metrics['accuracy']:.1f}% de acurácia geral")
    print(f"   • {analyzer.metrics['sensitivity']:.1f}% de sensibilidade")
    print(f"   • {analyzer.metrics['specificity']:.1f}% de especificidade")
    print(f"   • {analyzer.metrics['fp']} falsos positivos em {analyzer.metrics['adl_videos']} vídeos ADL")

if __name__ == "__main__":
    main()