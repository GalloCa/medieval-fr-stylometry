# MODULES
import os 
import requests 
import time

# FUNCTIONS 

def download_github_data(repo_url, local_dir):
    """
    Use recursivity in order to downlaod .txt files from a GitHub repository via API.

    Entrée : 
        repo_url (str) : URL de l'API du répertoire GitHub
        local_dir (str) : Chemin du dossier local pour l'enregistrement

    Sortie: 
        bool : True si le téléchargement est réussi, False sinon.
        Enregistrement des textes bruts.

    """
    GITHUB_TOKEN ='xxxxxxxxxxxxxxxxxxxxxxxxxx' # Besoin d'un token GitHub afin d'augmenter le nombre de requêtes possibles.
    headers = {'User-Agent': 'Mozilla/5.0', 'Authorization' : f'token {GITHUB_TOKEN}'}

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
    
    # 
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
            
        # Boucle : si élément est un fichier .txt alors téléchargement du contenu 
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

# MAIN 
repo_api_url = "https://api.github.com/repos/OpenMedFr/texts/contents"
local_storage = r"/workspaces/medFR-paleao-NLP/data/raw-texts"

if download_github_data(repo_api_url, local_storage):
    print("\nDownload complete. Files are in :", os.path.abspath(local_storage))
else:
    print('\nDownload failed due to API limits.')