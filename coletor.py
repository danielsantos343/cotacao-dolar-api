# Coleta a cotação do dólar na API do Banco Central (SGS),
# Trata os dados com pandas e salva em CSV.

from datetime import date
from pathlib import Path

import pandas as pd
import requests

class ColetorBCB:
    """Coleta e trata uma série do SGS (Sistema Gerenciador de Séries Temporais do Banco Central)."""

    URL_BASE = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados"

# Roda ao criar o objeto: guarda as informações iniciais
    def __init__(self,serie,data_inicial,data_final=None):
        self.serie = serie
        self.data_inicial = data_inicial

        # Se não informar a data final, usa a data de hoje
        self.data_final = data_final or date.today().strftime("%d/%m/%Y")
        self.dados = None       # ainda vazio; será preenchido em buscar()

# 1.Busca os dados na API e guarda numa tabela (DataFrame)
    def buscar(self):
        url = self.URL_BASE.format(serie=self.serie)
        parametros = {
            "formato":"json",
            "dataInicial":self.data_inicial,
            "dataFinal":self.data_final,
        }
        resposta = requests.get(url, params=parametros, timeout=30)
        resposta.raise_for_status()     # para o programa se a API der erro
        self.dados = pd.DataFrame(resposta.json())

# 2.Converte texto em data e em número
    def tratar(self):
        self.dados["data"] = pd.to_datetime(self.dados["data"],format="%d/%m/%Y") 
        self.dados["valor"] = pd.to_numeric(self.dados["valor"])

# 3.Calcula média, mínimo, máximo e variação por mês.
    def resumo_mensal(self):
        df=self.dados.copy()        #copia para não alterar os dados originais
        df["mes"] = df["data"].dt.to_period("M")
        mensal = df.groupby("mes")["valor"].agg(["mean","min","max","count"])
        mensal["variacao_pct"] = mensal["mean"].pct_change() * 100 
        mensal = mensal.reset_index()

    # Marca o mês atual como parcial (ainda não terminou)
        mes_atual = pd.Timestamp.today().to_period("M")
        mensal["mes_parcial"] = mensal["mes"] == mes_atual
        return mensal
# 4. Salva uma tabela em CSV no formato brasileiro (abre certo no EXCEL)
    def salvar(self, tabela, caminho):
        caminho = Path(caminho)
        caminho.parent.mkdir(exist_ok=True)     # cria a pasta se não existir 
        tabela.to_csv(caminho, sep=";", decimal=",", index=False, encoding="utf-8-sig")
        print(f"Arquivo salvo:{caminho}")

# Só roda quando o arquivo é executado diretamente (python coletor.py)
if __name__ == "__main__":
    coletor = ColetorBCB(serie=1, data_inicial="01/01/2024")    # cria o objeto
    coletor.buscar()
    coletor.tratar()

    print("Registros coletados:",len(coletor.dados))
    mensal = coletor.resumo_mensal()
    print(mensal.tail(6))

    coletor.salvar(coletor.dados, "dados/cotacao_dolar_diaria.csv")
    coletor.salvar(mensal, "dados/cotacao_dolar_mensal.csv")