"""
Module d'acquisition de données (scraping / API)

Ce script se charge de télécharger automatiquement le corpus de textes bruts depuis
un dépôt GitHub (Open Medieval French). Il utilise l'API GitHUB pour naviguer 
et extraire les fichier '.txt'.
Il ajoute un en-tête de citation standardisé à chaque fichier téléchargé

Dépendances :
    - requests : pour effectuer les appel HTTP vers l'API de GitHub
    - os : pour la création des répertoires locaux et gestion des chemins
    - time : pour temporiser les requêtes afin d'éviter le blocage (rate limiting)
"""

# MODULES
import os 
import requests 
import time

# FUNCTIONS 
def download_github_data(repo_url, local_dir):
    """
    Parcours un répertoire GitHub via son API pour télécharger tous 
    les fihciers .txt qu'il contient.

    Un token GitHub est utilisé pour augmenter la limite de requête de l'API
    publique. Chaque fichier téléchargé est enregitré localement.

    Entrée : 
        repo_url (str) : URL de l'API du répertoire GitHub
        local_dir (str) : Chemin du dossier local pour l'enregistrement

    Sortie: 
        bool : True si le téléchargement est réussi, False sinon.
        Enregistrement des textes bruts.

    """
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    if not GITHUB_TOKEN:
        print("Erreur : variable d'environnement GITHUB_TOKEN non définie.")
        print("Créer un fichier .env ou l'exporter avec : export GITHUB_TOKEN=ton_token")
        return False
    headers = {'User-Agent': 'Mozilla/5.0', 'Authorization': f'token {GITHUB_TOKEN}'}

    # Vérifie l'existence du dossier local et création s'il n'existe pas 
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    # Récupération du contenu du répertoire vie l'API GitHub
    resp = requests.get(repo_url, headers=headers)

    # Gestion des limites de requêtes sur GitHub
    if resp.status_code == 403:
        print('Rate limit exceeded (403)')
        return False
    elif resp.status_code != 200:
        print(f'Error fetching directory: {resp.status_code}')
        return False
    
    items = resp.json()
    if isinstance(items, dict):
        items = [items]

    for item in items:
        # Boucle d'appel récursif : si l'élément est un répertoire alors explore le sous-dossier
        if item['type'] == 'dir':
            new_local_dir = os.path.join(local_dir, item['name'])
            time.sleep(0.1)
            if not download_github_data(item['url'], new_local_dir):
                return False
            
        # Si élément est un fichier .txt alors téléchargement du contenu 
        elif item['type'] == 'file' and item['name'].endswith('.txt'):
            raw_text_url = item['download_url']
            file_path = os.path.join(local_dir, item['name'])

            print(f"Downloading raw texts : {item['name']}")

            file_data = requests.get(raw_text_url, headers=headers)
            if file_data.status_code == 200:
                # En-tête de citation
                citation_header = f'Citation: "{item["name"]}" (2018). Open Medieval French. https://github.com/OpenMedFr/texts\n'
                with open(file_path, mode = 'w', encoding ='utf-8') as f:
                    f.write(citation_header)
                    f.write("-" * 50 + "\n\n")
                    f.write(file_data.text)
            else:
                return False
    return True

