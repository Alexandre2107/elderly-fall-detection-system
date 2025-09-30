"""
Script para visualizar e analisar os resultados dos testes de detecção de quedas
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from datetime import datetime

def load_latest_results():
    """
    Carrega o arquivo de resultados mais recente
    """
    csv_files = glob.glob("fall_detection_results_*.csv")
    if not csv_files:
        csv_files = glob.glob("teste_rapido_resultados.csv")
    
    if not csv_files:
        print("❌ Nenhum arquivo de resultados encontrado!")
        return None
    
    latest_file = max(csv_files, key=os.path.getctime)
    print(f"📄 Carregando: {latest_file}")
    
    try:
        df = pd.read_csv(latest_file)
        return df, latest_file
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        return None, None

def analyze_results(df):
    """
    Analisa os resultados e gera estatísticas
    """
    print("\n" + "=" * 60)
    print("📊 ANÁLISE DETALHADA DOS RESULTADOS")
    print("=" * 60)
    
    total_videos = len(df)
    successful_detections = len(df[df['fall_detected'] == True])
    failed_detections = len(df[df['fall_detected'] == False])
    
    print(f"📁 Total de vídeos analisados: {total_videos}")
    print(f"✅ Quedas detectadas com sucesso: {successful_detections}")
    print(f"❌ Quedas não detectadas: {failed_detections}")
    print(f"📈 Taxa de detecção: {(successful_detections/total_videos)*100:.1f}%")
    
    # Análise dos tempos de detecção
    detected_df = df[df['fall_detected'] == True]
    if len(detected_df) > 0:
        print(f"\n⏱️ TEMPOS DE DETECÇÃO:")
        print(f"   Tempo médio: {detected_df['detection_time'].mean():.2f}s")
        print(f"   Tempo mínimo: {detected_df['detection_time'].min():.2f}s")
        print(f"   Tempo máximo: {detected_df['detection_time'].max():.2f}s")
        print(f"   Desvio padrão: {detected_df['detection_time'].std():.2f}s")
    
    # Análise dos tempos de processamento
    print(f"\n🔄 TEMPOS DE PROCESSAMENTO:")
    print(f"   Tempo médio de análise: {df['analysis_duration'].mean():.2f}s")
    print(f"   Tempo total de processamento: {df['analysis_duration'].sum():.2f}s")
    
    # Vídeos com problemas
    error_df = df[df['error'].notna() & (df['error'] != '')]
    if len(error_df) > 0:
        print(f"\n⚠️ VÍDEOS COM PROBLEMAS ({len(error_df)}):")
        for idx, row in error_df.iterrows():
            print(f"   {row['video']}: {row['error']}")
    
    # Listar vídeos não detectados
    not_detected_df = df[(df['fall_detected'] == False) & (df['error'].isna() | (df['error'] == ''))]
    if len(not_detected_df) > 0:
        print(f"\n❌ VÍDEOS SEM DETECÇÃO ({len(not_detected_df)}):")
        for idx, row in not_detected_df.iterrows():
            duration = f" ({row['video_duration']:.1f}s)" if pd.notna(row['video_duration']) else ""
            print(f"   {row['video']}{duration}")
    
    return df

def create_visualizations(df, filename_prefix=""):
    """
    Cria visualizações dos resultados
    """
    try:
        plt.style.use('default')
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Análise dos Resultados de Detecção de Quedas', fontsize=16, fontweight='bold')
        
        # 1. Gráfico de pizza - Taxa de detecção
        detection_counts = df['fall_detected'].value_counts()
        axes[0,0].pie(detection_counts.values, 
                     labels=['Detectado', 'Não Detectado'] if False in detection_counts.index else ['Detectado'],
                     autopct='%1.1f%%', 
                     colors=['#7fbf7f', '#ff7f7f'])
        axes[0,0].set_title('Taxa de Detecção de Quedas')
        
        # 2. Histograma - Tempos de detecção
        detected_df = df[df['fall_detected'] == True]
        if len(detected_df) > 0:
            axes[0,1].hist(detected_df['detection_time'], bins=10, color='skyblue', edgecolor='black', alpha=0.7)
            axes[0,1].set_title('Distribuição dos Tempos de Detecção')
            axes[0,1].set_xlabel('Tempo (segundos)')
            axes[0,1].set_ylabel('Número de Vídeos')
            axes[0,1].grid(True, alpha=0.3)
        else:
            axes[0,1].text(0.5, 0.5, 'Nenhuma detecção\npara mostrar', 
                          ha='center', va='center', transform=axes[0,1].transAxes)
            axes[0,1].set_title('Tempos de Detecção')
        
        # 3. Gráfico de barras - Detecções por vídeo
        video_results = df[['video', 'fall_detected']].copy()
        video_results['video_num'] = video_results['video'].str.extract(r'fall-(\d+)').astype(int)
        video_results = video_results.sort_values('video_num')
        
        colors = ['red' if not detected else 'green' for detected in video_results['fall_detected']]
        axes[1,0].bar(range(len(video_results)), video_results['fall_detected'].astype(int), color=colors, alpha=0.7)
        axes[1,0].set_title('Detecções por Vídeo')
        axes[1,0].set_xlabel('Vídeo (ordenado por número)')
        axes[1,0].set_ylabel('Queda Detectada (1=Sim, 0=Não)')
        axes[1,0].set_ylim(-0.1, 1.1)
        axes[1,0].grid(True, alpha=0.3)
        
        # 4. Scatter plot - Tempo de detecção vs duração do vídeo
        if len(detected_df) > 0:
            axes[1,1].scatter(detected_df['video_duration'], detected_df['detection_time'], 
                            c='blue', alpha=0.6, s=50)
            axes[1,1].set_title('Tempo de Detecção vs Duração do Vídeo')
            axes[1,1].set_xlabel('Duração do Vídeo (s)')
            axes[1,1].set_ylabel('Tempo de Detecção (s)')
            axes[1,1].grid(True, alpha=0.3)
            
            # Adicionar linha de referência (detecção no final do vídeo)
            max_duration = detected_df['video_duration'].max()
            axes[1,1].plot([0, max_duration], [0, max_duration], 'r--', alpha=0.5, label='Detecção no final')
            axes[1,1].legend()
        else:
            axes[1,1].text(0.5, 0.5, 'Nenhuma detecção\npara mostrar', 
                          ha='center', va='center', transform=axes[1,1].transAxes)
            axes[1,1].set_title('Tempo vs Duração')
        
        plt.tight_layout()
        
        # Salvar gráfico
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        chart_filename = f"{filename_prefix}analise_visual_{timestamp}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        print(f"📊 Gráficos salvos em: {chart_filename}")
        
        plt.show()
        
    except Exception as e:
        print(f"⚠️ Erro ao criar visualizações: {e}")
        print("   (Certifique-se de ter matplotlib instalado: pip install matplotlib)")

def main():
    """
    Função principal para análise dos resultados
    """
    print("=== ANÁLISE DE RESULTADOS DE DETECÇÃO DE QUEDAS ===")
    
    # Carregar dados
    result = load_latest_results()
    if result is None:
        return
    
    df, filename = result
    
    # Analisar resultados
    df_analyzed = analyze_results(df)
    
    # Criar visualizações
    print(f"\n📊 Criando visualizações...")
    create_visualizations(df_analyzed, "fall_detection_")
    
    # Opção de exportar relatório detalhado
    print(f"\n📋 RELATÓRIO DETALHADO:")
    print(f"   Arquivo original: {filename}")
    
    # Criar relatório em texto
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"relatorio_detalhado_{timestamp}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DETALHADO - SISTEMA DE DETECÇÃO DE QUEDAS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Arquivo fonte: {filename}\n\n")
        
        f.write("RESUMO GERAL:\n")
        f.write(f"Total de vídeos: {len(df)}\n")
        f.write(f"Quedas detectadas: {len(df[df['fall_detected'] == True])}\n")
        f.write(f"Taxa de sucesso: {(len(df[df['fall_detected'] == True])/len(df))*100:.1f}%\n\n")
        
        f.write("DETALHES POR VÍDEO:\n")
        f.write("-" * 60 + "\n")
        
        for idx, row in df.iterrows():
            status = "✅ DETECTADO" if row['fall_detected'] else "❌ NÃO DETECTADO"
            detection_info = f" (em {row['detection_time']:.1f}s)" if row['fall_detected'] and pd.notna(row['detection_time']) else ""
            error_info = f" - ERRO: {row['error']}" if pd.notna(row['error']) and row['error'] != '' else ""
            
            f.write(f"{row['video']}: {status}{detection_info}{error_info}\n")
    
    print(f"   Relatório completo: {report_filename}")

if __name__ == "__main__":
    main()