import os

# Chemin du dossier displex
displex_folder = "/home/pi/displex"

# Créer le dossier s'il n'existe pas
if not os.path.exists(displex_folder):
    os.makedirs(displex_folder)

# Chemin des fichiers config.py et player.py
config_path = os.path.join(displex_folder, "config.py")
player_path = os.path.join(displex_folder, "player.py")

# Supprimer les fichiers config.py et player.py s'ils existent
if os.path.exists(config_path):
    os.remove(config_path)
if os.path.exists(player_path):
    os.remove(player_path)

# Télécharger le fichier player.py depuis le dépôt GitHub
os.system(f"wget -O {player_path} https://raw.githubusercontent.com/aubrymedia/displx/main/player.py")

# Exécuter le script player.py
os.system(f"python3 {player_path}")
