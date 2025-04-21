import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os
import math

def bissecao(f, a, b, tol, max_iter=100):

    if f(a) * f(b) >= 0:
        return None, None, "Erro: f(a) e f(b) devem ter sinais opostos.", None
        
    tabela = []
    xn_ant = None
    
    for n in range(1, max_iter + 1):
        xn = (a + b) / 2
        fxn = f(xn)
        erro = abs(xn - xn_ant) if xn_ant is not None else None
        tabela.append((n, a, b, xn, fxn, erro))

        if fxn == 0 or (erro is not None and erro < tol):
            return xn, tabela, f"Raiz encontrada em x = {xn:.5f} após {n} iterações.", tol
        
        # Atualizar os limites
        if f(a) * fxn < 0:
            b = xn
        else:
            a = xn
        xn_ant = xn

    return xn, tabela, "Número máximo de iterações atingido.", tol

def plotar_bissecao(f, a, b, tol, raiz_exata=None, max_iter=100):
    # Executar o método da bisseção
    raiz_aprox, dados, msg, tol_usada = bissecao(f, a, b, tol, max_iter)

    if raiz_aprox is None:
        return None, None, msg
    
    # Criar DataFrame com os resultados
    colunas = ["n", "a_n", "b_n", "x_n", "f(x_n)", "erro"]
    df = pd.DataFrame(dados, columns=colunas)
    
    # pasta para salvar as imagens
    diretorio_projeto = os.path.dirname(os.path.abspath(__file__))  # Diretório do projeto onde o script está
    caminho_imagens = os.path.join(diretorio_projeto, "imagens-resultado")
    os.makedirs(caminho_imagens, exist_ok=True)

    # ----------- GERAR GRÁFICO ----------- 
    # definir um intervalo para o gráfico que captura bem a função
    x_min = min(a, b) - 0.5
    x_max = max(a, b) + 0.5
    x_vals = np.linspace(x_min, x_max, 1000)
    y_vals = [f(x) for x in x_vals]
    
    # criar figura com subplots (1 grande para o gráfico principal)
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # plotar a função
    ax.plot(x_vals, y_vals, 'b-', label='f(x)', linewidth=2)
    
    # adicionar linhas de referência
    ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.axvline(0, color='k', linestyle='-', alpha=0.3)
    
    # destacar a raiz aproximada
    ax.plot(raiz_aprox, f(raiz_aprox), 'ro', markersize=8, label=f'Raiz aproximada: {raiz_aprox:.5f}')
    
    if raiz_exata is not None:
        ax.plot(raiz_exata, f(raiz_exata), 'go', markersize=8, label=f'Raiz exata: {raiz_exata:.5f}')
    
    # visualizar os intervalos de cada iteração
    colors = plt.cm.viridis(np.linspace(0, 1, len(dados)))
    
    for i, (n, a_n, b_n, x_n, fx_n, erro) in enumerate(dados):
        # marcar o ponto médio de cada iteração
        ax.plot(x_n, fx_n, 'o', color=colors[i], markersize=6, alpha=0.7)
        
        # visualizar o intervalo [a_n, b_n]
        ax.plot([a_n, b_n], [f(a_n), f(b_n)], color=colors[i], alpha=0.5, 
                label=f'Iteração {n}' if i < 5 or i == len(dados)-1 else "")
        
        # adicionar linha vertical para cada iteração
        ax.vlines(x=x_n, ymin=min(0, fx_n), ymax=max(0, fx_n), 
                  linestyle='--', color=colors[i], alpha=0.5)
    
    # configurações do gráfico
    ax.set_title("Método da Bisseção", fontsize=16)
    ax.set_xlabel("x", fontsize=12)
    ax.set_ylabel("f(x)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # legenda
    ax.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    
    # salvamento do gráfico
    plt.savefig(os.path.join(caminho_imagens, "bissecao_completo.png"), dpi=300, bbox_inches="tight")
    
    # ----------- GERAR TABELA COMO IMAGEM ----------- 
    fig_tabela, ax_tabela = plt.subplots(figsize=(10, 2 + len(df) * 0.3))
    ax_tabela.axis('off')
    
    # formatar os dados para melhor visualização
    df_formatada = df.copy()
    # formatar números com 5 casas decimais para raiz e função, 4 para intervalos
    df_formatada['a_n'] = df_formatada['a_n'].apply(lambda x: f"{x:.4f}")
    df_formatada['b_n'] = df_formatada['b_n'].apply(lambda x: f"{x:.4f}")
    df_formatada['x_n'] = df_formatada['x_n'].apply(lambda x: f"{x:.5f}")
    df_formatada['f(x_n)'] = df_formatada['f(x_n)'].apply(lambda x: f"{x:.5f}")
    df_formatada['erro'] = df_formatada['erro'].apply(lambda x: f"{x:.5f}" if x is not None else "N/A")
    
    tabela_plot = ax_tabela.table(cellText=df_formatada.values,
                             colLabels=df_formatada.columns,
                             cellLoc='center',
                             loc='center')
    
    tabela_plot.auto_set_font_size(False)
    tabela_plot.set_fontsize(10)
    tabela_plot.scale(1.5, 1.2)
    
    # aplicando cores
    for i in range(len(df_formatada)):
        for j in range(len(df_formatada.columns)):
            cell = tabela_plot[i+1, j]
            if i % 2 == 0:
                cell.set_facecolor('#f0f0f0')
    
    plt.title("Dados das Iterações do Método da Bisseção", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(caminho_imagens, "tabela_bissecao.png"), dpi=300, bbox_inches="tight")
    
    # ----------- GERAR IMAGEM FINAL COMBINADA ----------- 
    img_width, img_height = 2000, 1600
    output_img = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))
    
    # carregar as imagens geradas
    grafico = Image.open(os.path.join(caminho_imagens, "bissecao_completo.png")).resize((img_width, img_height // 2), Image.LANCZOS)
    tabela = Image.open(os.path.join(caminho_imagens, "tabela_bissecao.png")).resize((img_width, img_height // 2), Image.LANCZOS)
    
    # combinar as imagens
    output_img.paste(grafico, (0, 0))
    output_img.paste(tabela, (0, img_height // 2))
    
    # título e informações
    draw = ImageDraw.Draw(output_img)
    try:
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        font = ImageFont.load_default()
    
    draw.text((img_width // 2, img_height - 50), msg, 
              fill=(0, 0, 0), font=font, anchor="mm")
    
    # salvando imagem final
    output_img.save(os.path.join(caminho_imagens, "bissecao_resultado_final.png"))
    
    return raiz_aprox, df, msg

# Exemplo de uso
if __name__ == "__main__":
    # Definir a função f(x)
    f = lambda x: x**2 - 3
    
    # Calcular a raiz exata para comparação
    raiz_exata = math.sqrt(3)
    
    # intervalo inicial e tolerância
    a = 1
    b = 2
    epsilon = 10**-1
    
    # executar e plotar
    raiz_aproximada, df_resultados, mensagem = plotar_bissecao(f, a, b, epsilon, raiz_exata)

# verificação de erro
if raiz_aproximada is None:
    print(mensagem)
else:
    print(mensagem)
    print(f"Raiz exata: {raiz_exata:.5f}")
    print(f"Raiz aproximada: {raiz_aproximada:.5f}")
    print(f"Tabela de iterações salva em 'imagens-resultado/tabela_bissecao.png'")
    print(f"Gráfico completo salvo em 'imagens-resultado/bissecao_completo.png'")
    print(f"Resultado final salvo em 'imagens-resultado/bissecao_resultado_final.png'")
