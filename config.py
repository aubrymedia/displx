import os
import subprocess
import urllib.request


def connect_to_wifi(ssid, password):
    # Modifiez le fichier wpa_supplicant.conf pour ajouter les informations du réseau WiFi
    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as f:
        f.write(f'network={{\n    ssid="{ssid}"\n    psk="{password}"\n}}\n')
    
    # Redémarrez le service wpa_supplicant pour appliquer les modifications
    subprocess.run(['sudo', 'systemctl', 'restart', 'dhcpcd.service'])
    subprocess.run(['sudo', 'systemctl', 'restart', 'wpa_supplicant.service'])


def download_and_run_script(url):
    # Téléchargez le script à partir de l'URL
    urllib.request.urlretrieve(url, 'player.py')
    
    # Exécutez le script
    subprocess.run(['python3', 'player.py'])


# Connectez-vous au réseau WiFi
connect_to_wifi('nom_du_reseau_wifi', 'mot_de_passe_wifi')

# Téléchargez et exécutez le script player.py depuis le dépôt GitHub
download_and_run_script('https://raw.githubusercontent.com/aubrymedia/displx/main/player.py')
