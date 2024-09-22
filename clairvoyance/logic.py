import os
import faiss
import numpy as np
import asyncio
import websockets
from langchain.embeddings import MistralEmbeddings
from dotenv import load_dotenv
from .models import MajorArcana

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# clé API Mistral
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError(
        "La clé API Mistral n'est pas définie. Assurez-vous que le fichier .env contient MISTRAL_API_KEY."
    )


# Charger l'index FAISS
def load_index(index_path):
    return faiss.read_index(index_path)


# Rechercher des vecteurs similaires
def search_vectors(index, query_vector, k=5):
    D, I = index.search(query_vector, k)
    return I, D


# Utiliser LangChain pour transformer le texte en vecteurs
def text_to_vector(text, api_key):
    embeddings = MistralEmbeddings(api_key=api_key)
    return np.array(embeddings.embed_text(text)).reshape(1, -1)


# Chemin vers l'index FAISS
index_path = "vector_index.faiss"

# Charger l'index FAISS
index = load_index(index_path)

# Dictionnaire pour stocker les sessions des utilisateurs
user_sessions = {}


async def interact_with_user(websocket, path):
    user_id = websocket.remote_address[
        1
    ]  # Utiliser l'adresse WebSocket comme identifiant de l'utilisateur
    if user_id not in user_sessions:
        user_sessions[user_id] = []

    async for message in websocket:
        # Ajouter le message de l'utilisateur à la session
        user_sessions[user_id].append(f"Utilisateur : {message}")

        # Créer le contexte en combinant les messages précédents
        context = "\n".join(user_sessions[user_id])

        # Prompt détaillé pour guider le LLM
        prompt = f"""
        Vous êtes un assistant virtuel spécialisé dans les consultations de tarot. Voici comment se déroule une consultation de tarot :

        1. **Introduction** :
           - Accueillez l'utilisateur et demandez-lui son nom.
           - Expliquez brièvement le processus de la consultation de tarot.

        2. **Choix du Thème** :
           - Demandez à l'utilisateur de choisir un thème pour la consultation. Les options disponibles sont :
             - Amour
             - Travail
             - Général

        3. **Tirage des Cartes** :
           - Demandez à l'utilisateur de couper le jeu en deux piles : gauche ou droite.
           - Demadez lui de choisir une des deux piles. on affiche le dos des cartes sur les deux piles il doit cliquer sur l'une des deux piles.
           - demandez lui le choix de tirage croix etc...
           - interpréter les cartes tirées.

        4. **Interprétation des Cartes** :
           - Fournissez les détails de la carte tirée, y compris :
             - Le nom de la carte
             - Les avertissements associés à la carte
             - La signification de la carte en matière d'amour, de travail et de manière générale
           - Affichez l'image de la carte.

        5. **Questions Suivantes** :
           - Invitez l'utilisateur à poser des questions supplémentaires ou à demander un autre tirage.

        6. **Conclusion** :
           - Remerciez l'utilisateur pour la consultation.
           - Offrez de l'aide supplémentaire si nécessaire.

        ### Exemple de Dialogue

        **Assistant** : Bonjour ! Je suis Mme T votre tarologue, avant de commencer la consultation du Tarot et obtenir vos réponses faisons connaissance. Quel est votre nom ?
        {context}
        """

        # Convertir l'entrée utilisateur en vecteur
        query_vector = text_to_vector(prompt, api_key)

        # Rechercher des vecteurs similaires dans l'index
        I, D = search_vectors(index, query_vector)

        # Utiliser les indices pour récupérer les informations pertinentes
        # et générer une réponse basée sur les vecteurs similaires
        # (Cette partie dépend de la structure de vos données et de la logique de votre application)
        # Par exemple, vous pouvez récupérer les cartes de tarot associées aux indices trouvés

        # Exemple de génération de réponse basée sur les vecteurs similaires
        response_message = f"Voici les résultats de votre recherche : {I}"

        # Ajouter la réponse de l'assistant à la session
        user_sessions[user_id].append(f"Assistant : {response_message}")

        # Envoyer la réponse au client
        await websocket.send(response_message)


# Démarrer le serveur WebSocket
start_server = websockets.serve(interact_with_user, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
