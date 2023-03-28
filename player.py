import os
import threading
import time
import requests
from bs4 import BeautifulSoup
import dropbox
import av

# URL de la page contenant le token d'accès
access_token_url = "https://aubrymedia.com/keyapi/"

# Récupération du contenu de la page
response = requests.get(access_token_url)
soup = BeautifulSoup(response.content, "html.parser")

# Extraction du token d'accès depuis la balise H1
access_token = soup.find("h1").text

dbx_folder = "/Displex"
local_folder = "/home/pi/contents"

# Crée le dossier local si nécessaire
if not os.path.exists(local_folder):
    os.makedirs(local_folder)

dbx = dropbox.Dropbox(access_token)

file_lock = threading.Lock()  # Ajouter un verrou pour les fichiers
downloaded_files = []  # Liste pour stocker les noms de fichiers téléchargés

def download_videos():
    global file_lock, downloaded_files

    result = dbx.files_list_folder(dbx_folder)

    for entry in result.entries:
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith(".mp4"):
            local_file_path = os.path.join(local_folder, entry.name)

            if entry.name not in downloaded_files:
                with open(local_file_path, "wb") as f:
                    metadata, res = dbx.files_download(entry.path_lower)
                    f.write(res.content)

                downloaded_files.append(entry.name)

    with file_lock:  # Acquérir le verrou avant de supprimer les fichiers
        local_files = list_files(local_folder)
        for file in local_files:
            if file not in downloaded_files:
                os.remove(os.path.join(local_folder, file))

def list_files(path):
    files = []
    for entry in os.scandir(path):
        if entry.is_file() and entry.name.endswith(".mp4"):
            files.append(os.path.join(path, entry.name))
    return files

def download_videos_loop():
    while True:
        download_videos()
        time.sleep(60)  # Télécharge les nouvelles vidéos toutes les 60 secondes

def play_videos():
    global file_lock

    while True:
        video_files = list_files(local_folder)

        if not video_files:
            continue

        instance = av.Player()

        for video_file in video_files:
            with file_lock:  # Acquérir le verrou avant d'ouvrir le fichier avec VLC
                stream = av.open(video_file).streams.video[0]
                instance.play(stream)

            while instance.playing:
                time.sleep(1)

                with file_lock:
                    current_video_files = list_files(local_folder)

                    if video_files != current_video_files:
                        break

if __name__ == "__main__":
    download_thread = threading.Thread(target=download_videos_loop)
    download_thread.start()

    play_videos()
