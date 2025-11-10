import requests as rq
# import tkinter as tk
import customtkinter as ctk

def pegar_cotacoes():
    requisicao = rq.get("https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL,BTC-BRL")

    requisicao_dic = requisicao.json()

    cotacao_dolar = requisicao_dic['USDBRL']['bid']
    cotacao_euro = requisicao_dic['EURBRL']['bid']
    cotacao_btc = requisicao_dic['BTCBRL']['bid']

    texto = f'''
    Dólar: {cotacao_dolar},
    Euro: {cotacao_euro},
    BTC: {cotacao_btc}'''

    print(texto)
    texto_cotacoes["text"] = texto


# ==========
ctk.set_appearance_mode("dark") # "dark", "light", "system"
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("Cotacao Atual das Moedas:")
janela.geometry("400x400")

texto_orientacao = ctk.CTkLabel(janela, text="Clique no botão pra ver as cotações das moedas")
texto_orientacao.grid(column=0, row=0, padx=10, pady=10)

texto_orientacao2 = ctk.CTkButton(janela, text="Buscar cotações Dólar/Euro/BTC", command=pegar_cotacoes)
texto_orientacao2.grid(column=0, row=1, padx=10, pady=10)

texto_cotacoes = ctk.CTkLabel(janela, text="")                       
texto_cotacoes.grid(column=0, row=2, padx=10, pady=10)
# texto_orientacao2 = tk.Label(janela, text="Clique aqui agora")
# texto_orientacao2.grid(column=0, row=2)

# pegar_cotacoes()


janela.mainloop()