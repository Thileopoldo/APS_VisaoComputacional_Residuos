"""Aplicação da APS: detecção de resíduos plásticos em praias e rios."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
import numpy as np


class DetectorResiduos:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("APS - Detecção de Resíduos Plásticos")
        self.root.geometry("560x260")
        self.root.resizable(False, False)

        self.image_rgb = None
        self.resultado = None
        self.caminho_imagem = None

        tk.Label(root, text="Detecção e Segmentação de Resíduos Plásticos",
                 font=("Arial", 15, "bold")).pack(pady=10)
        tk.Label(root, text="Selecione uma imagem de praia ou rio para analisar.").pack(pady=4)

        botoes = tk.Frame(root)
        botoes.pack(pady=10)
        tk.Button(botoes, text="1. Selecionar imagem", width=20,
                  command=self.selecionar_imagem).grid(row=0, column=0, padx=8)
        tk.Button(botoes, text="2. Processar imagem", width=20,
                  command=self.processar_imagem).grid(row=0, column=1, padx=8)
        tk.Button(botoes, text="Salvar resultado", width=20,
                  command=self.salvar_resultado).grid(row=1, column=0, padx=8, pady=8)
        tk.Button(botoes, text="Fechar aplicação", width=20,
                  command=self.fechar).grid(row=1, column=1, padx=8, pady=8)

        opcoes = tk.LabelFrame(root, text="Configurações", padx=12, pady=8)
        opcoes.pack(padx=20, pady=8, fill="x")

        tk.Label(opcoes, text="Espaço de cor:").grid(row=0, column=0, sticky="w")
        self.espaco_cor = tk.StringVar(value="Cinza")
        tk.Radiobutton(opcoes, text="Cinza", variable=self.espaco_cor,
                       value="Cinza").grid(row=0, column=1)
        tk.Radiobutton(opcoes, text="HSV", variable=self.espaco_cor,
                       value="HSV").grid(row=0, column=2)

        tk.Label(opcoes, text="Suavização (Gaussiano):").grid(row=1, column=0, sticky="w", pady=5)
        self.suavidade = tk.IntVar(value=5)
        tk.Scale(opcoes, from_=3, to=15, orient="horizontal", variable=self.suavidade,
                 resolution=2, length=190).grid(row=1, column=1, columnspan=2)

        self.status = tk.StringVar(value="Nenhuma imagem carregada.")
        tk.Label(root, textvariable=self.status, fg="blue", wraplength=520).pack(pady=5)

    def selecionar_imagem(self) -> None:
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
        )
        if not caminho:
            return

        imagem = cv2.imread(caminho)
        if imagem is None:
            messagebox.showerror("Erro", "Não foi possível carregar a imagem selecionada.")
            return

        self.caminho_imagem = caminho
        self.image_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        self.status.set(f"Imagem carregada: {os.path.basename(caminho)}")

    def processar_imagem(self) -> None:
        if self.image_rgb is None:
            messagebox.showwarning("Atenção", "Selecione uma imagem antes de processar.")
            return

        tamanho = int(self.suavidade.get())
        if tamanho % 2 == 0:
            tamanho += 1

        # Conversão do espaço de cor solicitada pela atividade.
        if self.espaco_cor.get() == "HSV":
            hsv = cv2.cvtColor(self.image_rgb, cv2.COLOR_RGB2HSV)
            canal_imagem = hsv[:, :, 1]
            legenda_cor = "HSV - Canal Saturacao"
        else:
            canal_imagem = cv2.cvtColor(self.image_rgb, cv2.COLOR_RGB2GRAY)
            legenda_cor = "Escala de Cinza"

        # Suavização Gaussiana para reduzir ruído antes da segmentação.
        filtrada = cv2.GaussianBlur(canal_imagem, (tamanho, tamanho), 0)

        # Otsu calcula automaticamente o limiar de separação.
        _, binaria = cv2.threshold(filtrada, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Inverte a máscara quando Otsu considera o fundo claro como objeto.
        borda = np.concatenate((binaria[0, :], binaria[-1, :],
                                binaria[:, 0], binaria[:, -1]))
        proporcao_borda_branca = np.mean(borda == 255)
        if proporcao_borda_branca > 0.60:
            binaria = cv2.bitwise_not(binaria)

        # Mantém apenas componentes com área suficiente para evitar falso ruído.
        binaria = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=1)
        binaria = cv2.morphologyEx(binaria, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8), iterations=2)

        contornos, _ = cv2.findContours(binaria, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contornos_validos = [c for c in contornos if cv2.contourArea(c) >= 20]

        area_pixels = sum(cv2.contourArea(c) for c in contornos_validos)
        area_total = binaria.shape[0] * binaria.shape[1]
        percentual = (area_pixels / area_total) * 100

        mascara_rgb = cv2.cvtColor(binaria, cv2.COLOR_GRAY2RGB)
        mascara_rgb[np.all(mascara_rgb == 255, axis=2)] = [255, 0, 0]
        sobreposta = cv2.addWeighted(self.image_rgb, 0.72, mascara_rgb, 0.28, 0)
        cv2.drawContours(sobreposta, contornos_validos, -1, (0, 255, 0), 2)

        texto_metricas = (f"Contornos: {len(contornos_validos)} | Area: {area_pixels:.0f} px "
                          f"({percentual:.2f}% da imagem)")
        cv2.putText(sobreposta, texto_metricas, (15, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.60, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.putText(sobreposta, texto_metricas, (15, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.60, (0, 0, 0), 1, cv2.LINE_AA)

        original = cv2.resize(self.image_rgb, (480, 320))
        filtrada_cor = cv2.cvtColor(filtrada, cv2.COLOR_GRAY2RGB)
        filtrada_cor = cv2.resize(filtrada_cor, (480, 320))
        binaria_cor = cv2.cvtColor(binaria, cv2.COLOR_GRAY2RGB)
        binaria_cor = cv2.resize(binaria_cor, (480, 320))
        sobreposta = cv2.resize(sobreposta, (480, 320))

        cv2.putText(original, "Original", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3)
        cv2.putText(original, "Original", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        cv2.putText(filtrada_cor, legenda_cor + " filtrada", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 3)
        cv2.putText(filtrada_cor, legenda_cor + " filtrada", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1)
        cv2.putText(binaria_cor, "Segmentacao Otsu", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3)
        cv2.putText(binaria_cor, "Segmentacao Otsu", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        cv2.putText(sobreposta, "Contornos detectados", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 3)
        cv2.putText(sobreposta, "Contornos detectados", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)

        painel_superior = np.hstack((cv2.cvtColor(original, cv2.COLOR_RGB2BGR), cv2.cvtColor(filtrada_cor, cv2.COLOR_RGB2BGR)))
        painel_inferior = np.hstack((cv2.cvtColor(binaria_cor, cv2.COLOR_RGB2BGR), cv2.cvtColor(sobreposta, cv2.COLOR_RGB2BGR)))
        painel = np.vstack((painel_superior, painel_inferior))

        self.resultado = painel
        self.status.set(texto_metricas)
        cv2.imshow("APS - Comparacao dos resultados", painel)
        cv2.setWindowProperty("APS - Comparacao dos resultados", cv2.WND_PROP_TOPMOST, 1)

    def salvar_resultado(self) -> None:
        if self.resultado is None:
            messagebox.showwarning("Atenção", "Processe uma imagem antes de salvar o resultado.")
            return

        destino = filedialog.asksaveasfilename(
            title="Salvar resultado",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        if destino:
            cv2.imwrite(destino, self.resultado)
            self.status.set(f"Resultado salvo em: {destino}")

    def fechar(self) -> None:
        cv2.destroyAllWindows()
        self.root.destroy()


if __name__ == "__main__":
    janela = tk.Tk()
    aplicativo = DetectorResiduos(janela)
    janela.protocol("WM_DELETE_WINDOW", aplicativo.fechar)
    janela.mainloop()
