import os
import subprocess
import shutil

CARPETA = r"audio/español"

# Localizar ffmpeg en el PATH actual
FFMPEG_BIN = r"C:\Users\JAVIER\anaconda3\envs\pruebaSolve\Library\bin\ffmpeg.exe"
if not FFMPEG_BIN:
    raise RuntimeError("❌ No se encontró ffmpeg en el PATH. Instálalo o verifica tu entorno.")

ARCHIVOS_ESPECIFICOS = [
    "gripe.mp3",
    "neumonia.mp3",
    "asma.mp3",
    "diabetes.mp3",
    "hipertension.mp3",
    "cancer.mp3",
    "diarrea.mp3",
    "covid_19.mp3",
    "anemia.mp3"
]

for archivo in ARCHIVOS_ESPECIFICOS:
    entrada = os.path.join(CARPETA, archivo)

    if not os.path.exists(entrada):
        print(f"❌ No se encontró: {entrada}")
        continue

    salida = os.path.join(CARPETA, f"temp_{archivo}")

    comando = [
        FFMPEG_BIN,   # 👈 aquí usamos la ruta absoluta encontrada
        "-y",
        "-i", entrada,
        "-acodec", "libmp3lame",
        "-ab", "192k",
        "-ar", "44100",
        "-ac", "2",
        salida
    ]

    print(f"🔄 Reparando {archivo}...")
    try:
        subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        os.remove(entrada)
        os.rename(salida, entrada)
        print(f"✅ {archivo} normalizado con éxito.")
    except subprocess.CalledProcessError:
        print(f"⚠️ Error al procesar {archivo}.")
