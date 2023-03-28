import os
import threading
import time
import requests
from bs4 import BeautifulSoup
import dropbox
import sqlite3
import av

if not os.path.exists('file_cache.db'):
    conn = sqlite3.connect('file_cache.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE files (name text)''')
    conn.close()

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

def list_files(path):
    files = []
    for entry in os.scandir(path):
        if entry.is_file() and entry.name.endswith(".mp4"):
            files.append(entry.name)
    return files

def download_videos(cursor):
    global file_lock

    result = dbx.files_list_folder(dbx_folder)

    for entry in result.entries:
        if isinstance(entry, dropbox.files.FileMetadata) and entry.name.endswith(".mp4"):
            local_file_path = os.path.join(local_folder, entry.name)

            if cursor.execute('SELECT * FROM files WHERE name=?', (entry.name,)).fetchone() is None:
                with open(local_file_path, "wb") as f:
                    metadata, res = dbx.files_download(entry.path_lower)
                    f.write(res.content)

                cursor.execute('INSERT INTO files VALUES (?)', (entry.name,))
                cursor.connection.commit()

    with file_lock:  # Acquérir le verrou avant de supprimer les fichiers
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
        download_videos(cursor)
        time.sleep(60)  # Télécharge les nouvelles vidéos toutes les 60 secondes

    conn.close()

def play_videos():
    global file_lock

    while True:
        container = av.open(local_folder)
        video_files = [f.name for f in container.streams.video]

        if not video_files:
            container.close()
            continue

        instance = av.Player()

        for video_file in video_files:
            with file_lock:  # Acquérir le verrou avant d'ouvrir le fichier avec VLC
                stream = container.streams.video[video_file]
                instance.play(stream)

            while instance.playing:
                time.sleep(1)

                with file_lock:
                    current_container = av.open(local_folder)
                    current_video_files = [f.name for f in current_container.streams.video]

                    if video_files != current_video_files:
                        container.close()
                        container = current_container
                        break

if __name__ == "__main__":
    download_thread = threading.Thread(target=download_videos_loop)
    download_thread.start()

    play_videos()
