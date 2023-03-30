import os

# Chemin du dossier displex
displex_folder = "/home/pi/displex"

# Créer le dossier s'il n'existe pas
if not os.path.exists(displex_folder):
    os.makedirs(displex_folder)

# Chemin du fichier player.py
player_path = os.path.join(displex_folder, "player.py")

# Supprimer le fichier player.py s'il existe
if os.path.exists(player_path):
    os.remove(player_path)

# Télécharger le fichier player.py depuis le dépôt GitHub
os.system(f"wget -O {player_path} https://raw.githubusercontent.com/aubrymedia/displx/main/player.py")

# Exécuter le script player.py
os.system(f"python3 {player_path}")
