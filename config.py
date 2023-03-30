import os

# Chemin du dossier displex
displex_folder = "/home/pi/displex"

# Créer le dossier s'il n'existe pas
if not os.path.exists(displex_folder):
    os.makedirs(displex_folder)

# Chemin du fichier player.py
player_path = os.path.join(displex_folder, "player.py")

# Télécharger le fichier player.py depuis le dépôt GitHub et remplacer la version existante s'il y en a une
os.system(f"wget -O {player_path} https://raw.githubusercontent.com/aubrymedia/displx/main/player.py")

# Exécuter le script player.py
os.system(f"python3 {player_path}")
