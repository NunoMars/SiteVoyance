import os
import logging
import time
import json
import re

import numpy as np
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from pgvector.django import L2Distance
from .models import MajorArcana, MajorArcanaVector

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if api_key := os.getenv("MISTRAL_API_KEY"):
    hf_token = os.getenv("HF_TOKEN")
else:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")

# Define the embedding model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
logger.info("Embedding model initialized")
model = ChatMistralAI(mistral_api_key=api_key)
logger.info("Language model initialized for summarization")


def extract_json(response):
    """Extrait la partie JSON valide de la réponse brute."""

    try:
        # Log de la réponse brute pour le débogage
        logger.debug("Réponse brute: %s", response)

        if not (json_match := re.search(r"\{.*\}", response, re.DOTALL)):
            raise ValueError("Aucun JSON valide trouvé.")
        json_data = json_match.group()

        # Supprimer les nouvelles lignes et les caractères supplémentaires
        json_data = re.sub(r"\n", "", json_data)

        try:
            return json.loads(json_data)
        except json.JSONDecodeError as inner_error:
            logger.error("Erreur de parsing JSON: %s", inner_error)
            raise ValueError(f"Erreur de parsing JSON : {inner_error}") from inner_error
    except Exception as e:
        logger.error(f"Erreur générale dans l'extraction JSON: {e}")
        raise ValueError(f"Erreur générale : {str(e)}") from e


def retry_with_backoff(func: callable, *args: tuple, **kwargs: dict) -> any:
    """Retry logic with exponential backoff."""
    max_retries = 5
    backoff_factor = 4
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if "429" in str(e):
                sleep_time = backoff_factor**attempt
                logger.info(
                    f"Retrying after {sleep_time} seconds due to too many requests..."
                )
                time.sleep(sleep_time)
            else:
                raise
    raise Exception("Max retries reached")


def voyante_chatbot(request, input_value):
    """Main function to handle tarot chatbot logic."""
    try:
        # Log the input value for debugging
        logger.debug(f"Input value: {input_value}")

        # Prepare the text for each card
        cards_list = input_value.get("list of chosed cards", [])

        cards = []

        # adding the card name to the list of cards and card image from MajorArcana
        for card in cards_list:
            card_name = MajorArcana.objects.get(card_name=card).card_name
            card_image = MajorArcana.objects.get(card_name=card_name).card_image.url
            cards.append({"card_name": card_name, "card_image": card_image})

        if not cards_list:
            logger.info(
                "No cards selected, using previous embeddings for the question."
            )
            return get_previous_draw(request, input_value)

        cards_with_vectors = MajorArcanaVector.objects.filter(
            card_id__card_name__in=cards_list
        )
        # Process with selected cards
        cards_text = []
        for card_vector in cards_with_vectors:
            card_text = card_vector.content
            cards_text.append(f"{card_vector.card_id.card_name}: {card_text}")

        full_text = "Tirage en croix:\n" + "\n".join(cards_text)
        logger.debug(f"Full text: {full_text}")

        # Utiliser L2Distance pour récupérer les voisins les plus proches
        question_embedding = embeddings.embed_query(input_value.get("question", ""))

        similar_vectors = MajorArcanaVector.objects.annotate(
            distance=L2Distance("embedding", question_embedding)
        ).order_by("distance")[:5]

        # Convertir les embeddings en listes
        # Formater correctement les documents
        documents = [
            Document(
                page_content=vector.content, metadata={"embedding": vector.embedding}
            )
            for vector in similar_vectors
        ]

        # Store the documents in the Django session
        request.session["documents"] = [
            {
                "page_content": vector.content,
                "metadata": {"embedding": vector.embedding.tolist()},
            }
            for vector in similar_vectors
        ]

        # Define the prompt template
        prompt = ChatPromptTemplate.from_template(
            """
            Comme Mme T tarologue, tu dois répondre aux questions des clients sur leur avenir en utilisant les cartes de tarot fournies dans le contexte et avec tout ce que tu connais sur la disposition en croix et les significations des cartes entre elles.
             Les cartes fournies sont : {cards_list} il y a le nom et l'url de l'image de la carte pour generer la réponse il ne faut pas changer ou traduire les noms des cartes ni les images car elles viennent directement de la base de données.
            Voici comment lire un tirage en croix :
            - La première carte représente votre situation actuelle.
            - La deuxième carte montre les difficultés et obstacles potentiels.
            - La troisième carte symbolise les événements futurs proches.
            - La quatrième carte apporte une réponse ou un éclairage sur la situation.
            - La cinquième carte résume la situation et offre une synthèse.

            Les cartes sont fournies dans le contexte avec leur signification et leur position dans le tirage en croix. Si tu as d'autres informations sur les cartes et le tirage de tarot en crois, tu peux les ajouter pour améliorer la réponse.

            Tu dois fournir une réponse uniquement en JSON strictement valide sans texte ou annotation autour. Le format doit correspondre à cet exemple exact :
            {{
                "carte1": {{
                    "nom": "La Situation",
                    "carte": "Nom de la carte",
                    "card_image": "URL de l'image de la carte",
                    "signification": "Signification de la carte"
                }},
                "carte2": {{
                    "nom": "Les Difficultés",
                    "carte": "Nom de la carte",
                    "card_image": "URL de l'image de la carte",
                    "signification": "Signification de la carte"
                }},
                "carte3": {{
                    "nom": "Les Événements",
                    "carte": "Nom de la carte",
                    "card_image": "URL de l'image de la carte",
                    "signification": "Signification de la carte"
                }},
                "carte4": {{
                    "nom": "La Réponse",
                    "carte": "Nom de la carte",
                    "card_image": "URL de l'image de la carte",
                    "signification": "Signification de la carte"
                }},
                "carte5": {{
                    "nom": "La Synthèse",
                    "carte": "Nom de la carte",
                    "card_image": "URL de l'image de la carte",
                    "signification": "Signification de la carte"
                }},
                "prediction": "Une prédiction basée sur l’ensemble des cartes tirées, tenant compte de leur position et de leur signification.",
                "reponse": "Une réponse personnalisée basée sur la question posée et les cartes tirées. Et proposer de répondre à des questions spécifiques en fonction des cartes tirées, questions sur différents thèmes."
            }}
            Le but est de fournir 5 cartes avec leur texte et sortir une prédiction en JSON sous la forme d'un dictionnaire fourni dans le prompt.
            <context>
            {context}
            </context>

            Question: {input}
        """
        )

        # Create the document and retrieval chains
        chain = create_stuff_documents_chain(model, prompt)

        # Pose une question spécifique en fonction des cartes tirées
        question = input_value.get("question", "Quelle est ma prédiction ?")

        try:
            response = chain.invoke(
                {
                    "input": question,
                    "context": documents,
                    "cards_list": cards_list,
                }
            )
            response_dict = extract_json(response)
        except Exception:
            # Retry with backoff si reponse pas complete
            response = retry_with_backoff(
                chain.invoke,
                {
                    "input": question,
                    "context": full_text,
                    "cards_list": cards_list,
                },
            )
            response_dict = extract_json(response)

        return {
            "subject": "prediction",
            "predictions": [response_dict],
        }

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"subject": "error", "message": str(e)}


def get_previous_draw(request, input_value):
    """Récupère le resultat de FAISS pour le tirage précédent qui contiens le tirage deja traité et redemande via un nouveau prompt de repondre."""

    question = input_value.get("question", "Quelle est ma prédiction ?")

    try:
        # Define the prompt template
        prompt = ChatPromptTemplate.from_template(
            """
            Comme Mme T tarologue, tu dois répondre aux questions des clients sur leur avenir en utilisant les cartes de tarot fournies dans le contexte et avec tout ce que tu connais sur la disposition en croix et les significations des cartes entre elles.
            Si tu a plus d'informations que celle fournies tu peux les utiliser a fin de mieux aider l'utilisateur, reponds uniquement en français et propose a l'utilisateur de poser une autre question.
            <context>
            {context}
            </context>

            Question: {input}
        """
        )

        # Create the document and retrieval chains
        document_chain = create_stuff_documents_chain(model, prompt)

        # Get documents in the Django session and create Document objects

        # Convertir les embeddings en listes avant de les stocker dans la session
        documents = [
            Document(
                page_content=doc["page_content"],
                metadata={"embedding": np.array(doc["metadata"]["embedding"])},
            )
            for doc in request.session.get("documents", [])
        ]

        # Pose une question spécifique en fonction des cartes tirées
        question = input_value.get("question", "Quelle est ma prédiction ?")
        response = document_chain.invoke({"input": question, "context": documents})

        # Use AIMessage to structure the response
        ai_message = AIMessage(content=response)

        # Vérifiez si la réponse est vide ou mal formée
        if not ai_message.content:
            raise ValueError("Empty response from the model")
        return {"subject": "chat", "chat": ai_message.content}
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"subject": "error", "message": str(e)}
