import os
import subprocess
import dropbox
import vlc
import time
import threading
import time
import requests
from bs4 import BeautifulSoup
import dropbox
import sqlite3
import av

# URL de la page contenant le token d'accès
access_token_url = "https://aubrymedia.com/keyapi/"

# Dossier Dropbox contenant les vidéos à télécharger
dbx_folder = "/"

# Dossier local où stocker les vidéos
local_folder = "/home/pi/videos"

# Verrou pour empêcher la lecture de vidéos en cours de téléchargement ou de suppression
file_lock = threading.Lock()

# Obtenez le jeton d'accès à l'API Dropbox en visitant la page access_token_url
access_token = requests.get(access_token_url).text.strip()

# Instancier le client Dropbox
dbx = dropbox.Dropbox(access_token)

def list_files(path):
    """
    Retourne une liste de noms de fichiers dans le dossier spécifié.
    """
    files = []
    for entry in os.scandir(path):
        if entry.is_file():
            files.append(entry.name)
    return files

def download_videos(cursor):
    global file_lock

    result = dbx.files_list_folder(dbx_folder)
    local_files = list_files(local_folder)

    for entry in result.entries:
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith(".mp4"):
            local_file_path = os.path.join(local_folder, entry.name)

            if entry.name not in local_files:
            if cursor.execute('SELECT * FROM files WHERE name=?', (entry.name,)).fetchone() is None:
                with open(local_file_path, "wb") as f:
                    metadata, res = dbx.files_download(entry.path_lower)
                    f.write(res.content)

            if entry.name in local_files:
                local_files.remove(entry.name)
                cursor.execute('INSERT INTO files VALUES (?)', (entry.name,))
                cursor.connection.commit()

    with file_lock:  # Acquérir le verrou avant de supprimer les fichiers
        for file in local_files:
            os.remove(os.path.join(local_folder, file))
        local_files = list_files(local_folder)
        for file in cursor.execute('SELECT * FROM files'):
            if file[0] not in local_files:
                os.remove(os.path.join(local_folder, file[0]))
                cursor.execute('DELETE FROM files WHERE name=?', (file[0],))
                cursor.connection.commit()

def download_videos_loop():
    conn = sqlite3.connect('file_cache.db')
    cursor = conn.cursor()

    while True:
        download_videos()
        download_videos(cursor)
        time.sleep(60)  # Télécharge les nouvelles vidéos toutes les 60 secondes

    conn.close()

def play_videos():
    global file_lock

    video_files = list_files(local_folder)
    while True:
        container = av.open(local_folder)
        video_files = [f.name for f in container.streams.video]

    if not video_files:
        return
        if not video_files:
            container.close()
            continue

    instance = vlc.Instance("--no-xlib")
    player = instance.media_player_new()
        instance = av.Player()

    while True:
        for video_file in video_files:
            with file_lock:  # Acquérir le verrou avant d'ouvrir le fichier avec VLC
                media = instance.media_new(os.path.join(local_folder, video_file))
                player.set_media(media)
            player.audio_toggle_mute()  # Désactiver l'audio
            player.play()
            player.set_fullscreen(True)
            time.sleep(1)

            while player.get_state() != vlc.State.Ended:
                stream = container.streams.video[video_file]
                instance.play(stream)

            while instance.playing:
                time.sleep(1)
                current_video_files = list_files(local_folder)
                if video_files != current_video_files:
                    video_files = current_video_files
                    player.stop()
                    break

            if player.get_state() == vlc.State.Ended:
                video_files = list_files(local_folder)

                with file_lock:
                    current_container = av.open(local_folder)
                    current_video_files = [f.name for f in current_container.streams.video]

                    if video_files != current_video_files:
                        container.close()
                        container = current_container
                        break

        container.close()

if __name__ == "__main__":
    download_thread = threading.Thread(target=download_videos_loop)
