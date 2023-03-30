import os

# Chemin du dossier displex
displex_folder = "/home/pi/displex"

# Créer le dossier s'il n'existe pas
if not os.path.exists(displex_folder):
    os.makedirs(displex_folder)

# Chemin du fichier config.py
config_path = os.path.join(displex_folder, "config.py")

# Supprimer le fichier config.py s'il existe
if os.path.exists(config_path):
    os.remove(config_path)

# Télécharger le fichier config.py depuis le dépôt GitHub
os.system(f"wget -O {config_path} https://raw.githubusercontent.com/aubrymedia/displx/main/config.py")

# Exécuter le script config.py
os.system(f"python3 {config_path}")
