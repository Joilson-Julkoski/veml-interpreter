import os
import subprocess

PALAVRAS_TXT = "palavras.txt"
IMAGEM = "fundo.jpeg"
AUDIO = "teste.mp3"
VIDEO_TEMP = "video_temp.mp4"
VIDEO_FINAL = "video_final.mp4"
FPS = 30


def limpar():
    arquivos = [VIDEO_TEMP]
    for a in arquivos:
        if os.path.exists(a):
            os.remove(a)


def ler_palavras(caminho):
    palavras = []
    with open(caminho, "r", encoding="utf-8") as f:
        linhas = f.readlines()

    for i, linha in enumerate(linhas):
        tempo, palavra = linha.strip().split(":", 1)
        inicio = float(tempo.strip())
        palavra = palavra.strip()

        # define o fim como o início da próxima palavra
        if i < len(linhas) - 1:
            prox_tempo = float(linhas[i + 1].split(":")[0])
            fim = prox_tempo
        else:
            fim = inicio + 0.6  # fallback da última palavra

        palavras.append((inicio, fim, palavra))

    return palavras


def adicionar_texto(palavras):
    filtros = []

    for inicio, fim, palavra in palavras:
        filtros.append(
            f"drawtext=text='{palavra}':"
            f"fontcolor=white:fontsize=64:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"enable='between(t,{inicio},{fim})'"
        )

    return ",".join(filtros)


def adicionar_imagem():
    return [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", IMAGEM,
        "-t", "60",
        "-vf", "scale=1280:720",
        "-r", str(FPS),
        VIDEO_TEMP
    ]


def gerar_video():
    palavras = ler_palavras(PALAVRAS_TXT)
    filtros_texto = adicionar_texto(palavras)

    cmd = [
        "ffmpeg",
        "-y",
        "-loop", "1",
        "-i", IMAGEM,
        "-i", AUDIO,
        "-vf", f"scale=1280:720,{filtros_texto}",
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
