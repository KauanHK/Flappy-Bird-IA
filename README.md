# Flappy Bird-IA

## Visão Geral
Este projeto implementa um algoritmo genético para treinar redes neurais a jogarem Flappy Bird. 
A IA utiliza técnicas evolutivas para melhorar o desempenho dos pássaros ao longo de múltiplas gerações.

## Parâmetros Padrões de Treinamento
- Número de Pássaros: 100
- Porcentagem de Elite: 20%
- Porcentagem de Pássaros Aleatórios: 10%
- Taxa de Mutação: 0,1
- Força de Mutação: 0,2

## Pré-requisitos
- Python 3.8+
- Pygame
- NumPy

## Instalação
```bash
git clone https://github.com/KauanHK/Flappy-Bird-IA.git
pip install pygame numpy
```

## Executando o Treinamento
```bash
python src/main.py
```

## Processo de Treinamento
1. Inicializar população de redes neurais
2. Simular desempenho dos pássaros
3. Selecionar pássaros com melhor desempenho
4. Criar nova geração através de:
   - Elitismo
   - Cruzamento
   - Inserção aleatória
   - Mutação
