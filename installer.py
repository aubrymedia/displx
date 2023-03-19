import dropbox
import os
import requests
import subprocess
from bs4 import BeautifulSoup

# Configuration
url = "https://aubrymedia.com/keyapi"
dbx_folder = "/Script"
local_folder = "/home/displex"
file_name = "installer.py"

# Récupération de l'access token depuis la balise H1 de l'URL
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
access_token = soup.h1.text.strip()

# Initialisation du client Dropbox
dbx = dropbox.Dropbox(access_token)

# Récupération du bon chemin du fichier
entries = dbx.files_list_folder(dbx_folder).entries
file_path = None
for entry in entries:
    if isinstance(entry, dropbox.files.FileMetadata) and entry.name == file_name:
        file_path = entry.path_lower
        break

if file_path is None:
    raise FileNotFoundError(f"Le fichier {file_name} est introuvable dans {dbx_folder}.")

# Téléchargement du fichier
local_file_path = os.path.join(local_folder, file_name)

with open(local_file_path, "wb") as local_file:
    _, res = dbx.files_download(file_path)
    local_file.write(res.content)

print(f"Fichier {file_name} téléchargé avec succès dans {local_folder}.")

# Exécution du fichier téléchargé
subprocess.call(["python", local_file_path])
