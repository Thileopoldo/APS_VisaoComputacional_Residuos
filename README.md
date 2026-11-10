# APS - Detecção de Resíduos Plásticos

Aplicação em Python para a APS de Processamento Digital de Imagens e Visão Computacional (UNIP).

##Video

https://youtu.be/8A9xvoVNKck video de apresentação

## Tema

Detecção e segmentação automática de resíduos plásticos em praias e rios.

## Pré-requisitos

- Python 3.9 ou superior
- Tkinter instalado com o Python (normalmente já vem no Windows)

## Instalação

```powershell
py -m pip install -r requirements.txt
```

## Execução

```powershell
py main.py
```

1. Clique em **Selecionar imagem**.
2. Escolha escala de cinza ou canal de saturação HSV.
3. Ajuste o tamanho do filtro Gaussiano.
4. Clique em **Processar imagem**.
5. Consulte a imagem original, a imagem filtrada, a máscara Otsu e o resultado com contornos.
6. Use **Salvar resultado** para exportar o painel.

A aplicação conta contornos válidos (área mínima de 20 pixels), calcula sua área total e informa a porcentagem da imagem ocupada pela segmentação.

## Observação

A segmentação por limiar é uma técnica didática. Ambientes externos possuem grande variação de luz, água e textura; resultados melhores podem exigir ajustes ou um modelo treinado.
