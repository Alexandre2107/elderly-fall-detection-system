# Sistema de Teste de Falsos Positivos - Vídeos ADL

Esta pasta contém os scripts para testar **falsos positivos** no sistema de detecção de quedas usando vídeos ADL (Activities of Daily Living).

## 🎯 Objetivo dos Testes ADL

Os vídeos ADL mostram **atividades normais do dia a dia** como:

- Caminhar
- Sentar e levantar
- Agachar para pegar objetos
- Exercícios leves
- Atividades domésticas

**IMPORTANTE:** Esses vídeos **NÃO devem** ser detectados como quedas. Se forem detectados, são **falsos positivos**.

## 📂 Arquivos na Pasta

### 1. `adl_test_automated.py`

**Função:** Teste automatizado de todos os 40 vídeos ADL

- Processa todos os vídeos da pasta `data_set_videos_ADL`
- Identifica falsos positivos
- Calcula especificidade do sistema
- Gera relatório CSV detalhado

### 2. `teste_rapido_adl.py`

**Função:** Teste rápido com 8 vídeos ADL selecionados

- Validação rápida antes do teste completo
- Útil para ajustar parâmetros

### 3. `analise_completa_precisao.py`

**Função:** Análise combinada de quedas reais + ADL

- Combina resultados dos dois tipos de teste
- Calcula métricas completas de precisão
- Gera visualizações avançadas

## 🚀 Como Executar os Testes

### Passo 1: Teste Rápido ADL (8 vídeos)

```bash
python data_set_ADL_codes/teste_rapido_adl.py
```

### Passo 2: Teste Completo ADL (40 vídeos)

```bash
python data_set_ADL_codes/adl_test_automated.py
```

### Passo 3: Análise Completa (Quedas + ADL)

```bash
python data_set_ADL_codes/analise_completa_precisao.py
```

## 📊 Métricas Importantes

### **Especificidade**

- **O que é:** Capacidade de NÃO detectar quedas em atividades normais
- **Fórmula:** Verdadeiros Negativos / (Verdadeiros Negativos + Falsos Positivos)
- **Meta:** >95% (menos de 5% de falsos positivos)

### **Taxa de Falsos Positivos**

- **O que é:** Porcentagem de vídeos ADL incorretamente detectados como quedas
- **Fórmula:** Falsos Positivos / Total de ADL
- **Meta:** <5%

## 📈 Interpretação dos Resultados

### ✅ **Resultados Bons:**

- Especificidade >95%
- 0-2 falsos positivos em 40 vídeos ADL
- Sistema confiável para uso prático

### ⚠️ **Resultados Moderados:**

- Especificidade 85-95%
- 2-6 falsos positivos
- Considerar ajustar parâmetros

### ❌ **Resultados Ruins:**

- Especificidade <85%
- > 6 falsos positivos
- Sistema precisa de ajustes significativos

## 🔧 Ajustes para Reduzir Falsos Positivos

Se a taxa de falsos positivos estiver alta, considere:

1. **Aumentar thresholds:**

   ```python
   Y_VELOCITY_THRESHOLD = 8          # Era 5
   TRUNK_HORIZONTAL_THRESHOLD = 45   # Era 35
   LOWER_BODY_THRESHOLD = 0.75      # Era 0.65
   ```

2. **Aumentar tempo de confirmação:**

   ```python
   FALL_CONFIRM_TIME = 2.0          # Era 1.0
   ```

3. **Lógica mais restritiva:**
   - Exigir mais condições simultâneas
   - Adicionar filtros de movimento
   - Considerar histórico temporal

## 📋 Exemplo de Saída Esperada

```
=== TESTE DE FALSOS POSITIVOS - VÍDEOS ADL ===
[1/40] adl-01-cam0.mp4: ✅ Normal - Nenhuma queda detectada
[2/40] adl-02-cam0.mp4: ✅ Normal - Nenhuma queda detectada
[3/40] adl-03-cam0.mp4: ❌ FALSO POSITIVO detectado em 3.2s
...
[40/40] adl-40-cam0.mp4: ✅ Normal - Nenhuma queda detectada

RESUMO ADL: 2/40 falsos positivos (5.0%)
ESPECIFICIDADE: 95.0% (meta: >95%)

📈 MÉTRICAS DE QUALIDADE:
🎯 Especificidade: 95.0% (meta: >95%)
✅ BOM: Taxa aceitável de falsos positivos
```

## 🎯 Análise Completa de Precisão

Após executar os testes de quedas reais E ADL, execute:

```bash
python data_set_ADL_codes/analise_completa_precisao.py
```

Isso gerará:

- **Matriz de confusão completa**
- **Métricas de precisão, sensibilidade e especificidade**
- **Gráficos detalhados**
- **Relatório executivo**

### Métricas da Análise Completa:

- **Sensibilidade:** % de quedas reais detectadas
- **Especificidade:** % de ADL não detectadas como quedas
- **Precisão:** Das detecções, % que são realmente quedas
- **Acurácia:** % geral de acertos
- **F1-Score:** Média harmônica entre precisão e sensibilidade

## 🛠️ Solução de Problemas

### "Muitos falsos positivos"

- Ajustar thresholds para serem mais restritivos
- Aumentar tempo de confirmação
- Revisar lógica de detecção

### "Sistema muito conservador"

- Se especificidade >98% mas sensibilidade <70%
- Considerar reduzir alguns thresholds
- Balancear entre sensibilidade e especificidade

## 📁 Arquivos Gerados

- `adl_false_positive_results_YYYYMMDD_HHMMSS.csv`
- `teste_rapido_adl_resultados.csv`
- `relatorio_completo_precisao_YYYYMMDD_HHMMSS.txt`
- `analise_completa_precisao_YYYYMMDD_HHMMSS.png`

## 🎯 Meta Final

**Sistema ideal para detecção de quedas:**

- Sensibilidade >80% (detecta a maioria das quedas reais)
- Especificidade >95% (poucos falsos positivos)
- Acurácia geral >85%
- Balanceamento entre detectar quedas e evitar alarmes falsos
