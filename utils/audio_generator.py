import json
import os
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 150)  

palabra = "anemia"
texto = palabra
path_audio = f"audio/español/{palabra}.mp3"

print(f"Generando: {texto} → {path_audio}")
engine.save_to_file(texto, path_audio)

engine.runAndWait()
print("Audios generados correctamente.")
