from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd
import matplotlib.pyplot as plt

SITE1 = 'https://devaprender-play.netlify.app/'

def main():
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(SITE1)

    wait = WebDriverWait(driver, 10)

    try:
        produtos = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//h3[contains(@class, 'text-lg')]")))
        precos = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//p[contains(@class, 'text-2xl')]")))
        categorias = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//p[contains(@class, 'text-gray-500 text-sm mb-2')]")))
    except Exception as e:
        print(f"Erro ao capturar os elementos: {e}")
        driver.quit()
        return

    with open('precos.csv', 'w', encoding='utf-8') as arquivo:
        for produto, preco, categoria in zip(produtos, precos, categorias):
            arquivo.write(f'{produto.text},{preco.text},{categoria.text}{os.linesep}')

    driver.quit()

    df = pd.read_csv("precos.csv", names=["Produto", "Preço", "Categoria"])

    df["Preço"] = df["Preço"].replace(r"[^\d,\.]", "", regex=True).str.replace(",", ".").astype(float)

    categorias_unicas = df["Categoria"].unique()
    cores = plt.cm.get_cmap("tab10", len(categorias_unicas))
    cor_categoria = {cat: cores(i) for i, cat in enumerate(categorias_unicas)}

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(df)), df["Preço"], color=[cor_categoria[cat] for cat in df["Categoria"]])

    plt.title("Comparação de Preços por Categoria")
    plt.xlabel("Produto")
    plt.ylabel("Preço")
    plt.xticks([])
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    handles = [plt.Rectangle((0, 0), 1, 1, color=cor_categoria[cat]) for cat in categorias_unicas]
    plt.legend(handles, categorias_unicas, title="Categorias")

    def on_click(event):
        for bar, (produto, preco) in zip(bars, zip(df["Produto"], df["Preço"])):
            if bar.contains(event)[0]:
                print(f"Produto: {produto}, Preço: {preco}")
                break

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()


if __name__ == '__main__':
    main()
