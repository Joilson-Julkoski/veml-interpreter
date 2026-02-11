import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

url = "https://api.lemonfox.ai/v1/audio/transcriptions"
headers = {
  "Authorization": f"Bearer {config['LEAMON_FOX_API_KEY']}"
}

data = {
  "language": "portuguese",
  "response_format": "verbose_json",
  "timestamp_granularities[]": "word"
}


files = {"file": open("teste.mp3", "rb")}
response = requests.post(url, headers=headers, files=files, data=data)
data = response.json()

def extrair_palavras_e_tempos(transcricao):
    resultado = []

    for segment in transcricao.get("segments", []):
        for word in segment.get("words", []):
            resultado.append({
                "palavra": word.get("word"),
                "inicio": word.get("start"),
                "fim": word.get("end")
            })

    return resultado


def salvar_palavras_em_txt(palavras, caminho_txt):
    with open(caminho_txt, "w", encoding="utf-8") as f:
        for item in palavras:
            inicio = item["inicio"]
            palavra = item["palavra"]
            f.write(f"{inicio:.2f}: {palavra}\n")

only_words = extrair_palavras_e_tempos(data)

salvar_palavras_em_txt(only_words, "palavras.txt")


# To upload a local file add the files parameter:
