import os

# Installez les bibliothèques nécessaires
os.system('sudo apt-get update')
os.system('sudo apt-get install -y dropbox vlc python3-pip')
os.system('pip3 install requests beautifulsoup4')

# Téléchargez le script player.py depuis le dépôt GitHub
os.system('wget https://raw.githubusercontent.com/aubrymedia/displx/main/player.py')

# Exécutez le script player.py
os.system('python3 player.py')
