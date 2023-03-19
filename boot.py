import os
import urllib.request

# Téléchargez le script player.py depuis le dépôt GitHub
urllib.request.urlretrieve('https://raw.githubusercontent.com/aubrymedia/displx/main/player.py', 'player.py')

# Exécutez le script player.py
os.system('python3 player.py')
