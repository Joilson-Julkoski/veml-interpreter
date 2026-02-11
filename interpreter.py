import os
import subprocess

PALAVRAS_TXT = "palavras.txt"
IMAGEM = "fundo.jpeg"
AUDIO = "ia.wav"
VIDEO_FINAL = "video_final.mp4"
FPS = 60

import requests
import os
import hashlib
from dotenv import dotenv_values

config = dotenv_values(".env")
PEXELS_API_KEY = config['PEXELS_KEY']
PASTA_IMAGENS = "imagens_cache"

os.makedirs(PASTA_IMAGENS, exist_ok=True)


def baixar_imagem(keyword):
    # cria nome fixo baseado na palavra (cache)
    nome_arquivo = hashlib.md5(keyword.encode()).hexdigest() + ".jpg"
    caminho = os.path.join(PASTA_IMAGENS, nome_arquivo)

    # se já baixou antes, reutiliza
    if os.path.exists(caminho):
        return caminho

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": keyword, "per_page": 1}

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print("Erro ao buscar imagem:", response.text)
        return None

    data = response.json()

    if not data["photos"]:
        print("Nenhuma imagem encontrada para:", keyword)
        return None

    imagem_url = data["photos"][0]["src"]["large"]

    img_data = requests.get(imagem_url).content
    with open(caminho, "wb") as f:
        f.write(img_data)

    return caminho



def limpar():
    if os.path.exists(VIDEO_FINAL):
        os.remove(VIDEO_FINAL)


def ler_palavras(caminho):
    eventos = []

    with open(caminho, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    for i, linha in enumerate(linhas):
        tempo, conteudo = linha.strip().split(":", 1)
        inicio = float(tempo.strip())
        conteudo = conteudo.strip()

        if i < len(linhas) - 1:
            prox_tempo = float(linhas[i + 1].split(":")[0])
            fim = prox_tempo
        else:
            fim = inicio + 0.6

        # Detecta comando especial
        if "[" in conteudo and "]" in conteudo:
            comando = conteudo.split("[")[1].split("]")[0]

            if comando.lower() == "clean":
                eventos.append((inicio, fim, "clean", None))
            else:
                eventos.append((inicio, fim, "image", baixar_imagem(comando)))
        else:
            eventos.append((inicio, fim, "text", conteudo))

    return eventos


def escapar_texto(texto):
    return (
        texto.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
    )


def gerar_video():
    eventos = ler_palavras(PALAVRAS_TXT)

    filtros = []
    filtro_base = "[0:v]scale=1280:720[base];"
    ultimo_label = "[base]"
    contador_img = 0

    for inicio, fim, tipo, valor in eventos:

        if tipo == "text":
            texto = escapar_texto(valor)
            label_out = f"[v{contador_img}]"

            filtros.append(
                f"{ultimo_label}drawtext=text='{texto}':"
                f"fontcolor=white:fontsize=64:"
                f"x=(w-text_w)/2:y=(h-text_h)/2:"
                f"enable='between(t,{inicio},{fim})'"
                f"{label_out};"
            )

            ultimo_label = label_out
            contador_img += 1

        elif tipo == "image":
            label_img = f"[img{contador_img}]"
            label_out = f"[v{contador_img}]"

            filtros.append(
                f"movie='{valor}',scale=400:-1{label_img};"
                f"{ultimo_label}{label_img}overlay="
                f"(W-w)/2:(H-h)/2:"
                f"enable='between(t,{inicio},{fim})'"
                f"{label_out};"
            )

            ultimo_label = label_out
            contador_img += 1

        elif tipo == "clean":
            # Apenas não aplica overlay novo
            continue

    filtro_complexo = filtro_base + "".join(filtros)

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", IMAGEM,
        "-i", AUDIO,
        "-filter_complex", filtro_complexo,
        "-map", ultimo_label,
        "-map", "1:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        VIDEO_FINAL
    ]

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    limpar()
    gerar_video()
    print("🎬 Vídeo gerado com sucesso:", VIDEO_FINAL)
