import os
import dropbox
import vlc
import time
import threading
import requests
from bs4 import BeautifulSoup

# URL de la page contenant le token d'accès
access_token_url = "https://aubrymedia.com/keyapi/"

# Récupération du contenu de la page
response = requests.get(access_token_url)
soup = BeautifulSoup(response.content, "html.parser")

# Extraction du token d'accès depuis la balise H1
access_token = soup.find("h1").text
dbx_folder = "/Displex"
local_folder = "C:/Users/aubry/Desktop/DISPLEXCOM/contents"

dbx = dropbox.Dropbox(access_token)

file_lock = threading.Lock()  # Ajouter un verrou pour les fichiers

def list_files(path):
    files = []
    for entry in os.scandir(path):
        if entry.is_file() and entry.name.endswith(".mp4"):
            files.append(entry.name)
    return files

def download_videos():
    global file_lock

    result = dbx.files_list_folder(dbx_folder)
    local_files = list_files(local_folder)

    for entry in result.entries:
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith(".mp4"):
            local_file_path = os.path.join(local_folder, entry.name)

            if entry.name not in local_files:
                with open(local_file_path, "wb") as f:
                    metadata, res = dbx.files_download(entry.path_lower)
                    f.write(res.content)

            if entry.name in local_files:
                local_files.remove(entry.name)

    with file_lock:  # Acquérir le verrou avant de supprimer les fichiers
        for file in local_files:
            os.remove(os.path.join(local_folder, file))

def download_videos_loop():
    while True:
        download_videos()
        time.sleep(20)  # Télécharge les nouvelles vidéos toutes les 60 secondes

def play_videos():
    global file_lock

    video_files = list_files(local_folder)

    if not video_files:
        return

    instance = vlc.Instance("--no-xlib")
    player = instance.media_player_new()

    while True:
        for video_file in video_files:
            with file_lock:  # Acquérir le verrou avant d'ouvrir le fichier avec VLC
                media = instance.media_new(os.path.join(local_folder, video_file))
                player.set_media(media)
            player.play()
            player.set_fullscreen(True)
            time.sleep(1)

            while player.get_state() != vlc.State.Ended:
                time.sleep(1)
                current_video_files = list_files(local_folder)
                if video_files != current_video_files:
                    video_files = current_video_files
                    player.stop()
                    break

            if player.get_state() == vlc.State.Ended:
                video_files = list_files(local_folder)

if __name__ == "__main__":
    download_thread = threading.Thread(target=download_videos_loop)
    download_thread.start()

    play_videos()
