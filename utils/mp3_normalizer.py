import os
import subprocess

CARPETA = "audio/español"

for archivo in os.listdir(CARPETA):
    if archivo.lower().endswith(".mp3"):
        entrada = os.path.join(CARPETA, archivo)
        salida = os.path.join(CARPETA, f"temp_{archivo}")

        comando = [
            "ffmpeg",
            "-y",
            "-i", entrada,
            "-acodec", "libmp3lame",
            "-ab", "192k",     
            "-ar", "44100",    
            "-ac", "2",      
            salida
        ]

        print(f"Reparando {archivo}...")
        subprocess.run(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        os.remove(entrada)
        os.rename(salida, entrada)

print("Todos los .mp3 han sido convertidos a versión compatible con pygame.")
