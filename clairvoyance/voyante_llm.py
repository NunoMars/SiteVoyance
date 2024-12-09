import os
import logging
import time
import json
import re

from django.contrib.sessions.models import Session
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from .models import MajorArcana

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if api_key := os.getenv("MISTRAL_API_KEY"):
    hf_token = os.getenv("HF_TOKEN")
else:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")


def retry_with_backoff(func, *args, **kwargs):
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


def voyante_chatbot(input_value):
    """Main function to handle tarot chatbot logic."""
    try:

        # Log the input value for debugging
        logger.debug(f"Input value: {input_value}")

        # Prepare the text for each card
        cards_list = input_value.get("list of chosed cards", [])
        if not cards_list:
            raise ValueError("No cards selected")

        cards_text = []
        model = ChatMistralAI(mistral_api_key=api_key)
        logger.info("Language model initialized for summarization")

        cards_text = []
        for card in cards_list:
            try:
                card_text = MajorArcana.objects.get(card_name_fr=card).card_text()
                cards_text.append(f"{card}: {card_text}")
            except MajorArcana.DoesNotExist:
                logger.warning(f"Carte {card} non trouvée dans la base de données.")
                cards_text.append(f"{card}: [Carte non trouvée]")
        queryset = MajorArcana.objects.filter(card_name_fr__in=cards_list)

        cards = [
            {
                "name": card.card_name_fr,
                "image_url": card.card_image.url,
            }
            for card in queryset
        ]
        # Prepare the full text for the API
        full_text = "Tirage en croix:\n" + "\n".join(cards_text)
        logger.debug(f"Full text: {full_text}")
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500)
        split_texts = text_splitter.split_text(full_text)
        split_documents = [Document(page_content=chunk) for chunk in split_texts]

        # Define the embedding model
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        logger.info("Embedding model initialized")

        # Create the vector store with retry logic
        vector = retry_with_backoff(FAISS.from_documents, split_documents, embeddings)
        logger.info(f"Vector store created with {len(split_documents)} documents.")

        # Define a retriever interface with custom search parameters
        retriever = vector.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        )

        # Define the prompt template
        prompt = ChatPromptTemplate.from_template(
            """
            Comme Mme T tarologue, tu dois répondre aux questions des clients sur leur avenir en utilisant les cartes de tarot fournies dans le contexte et avec tout ce que tu connais sur la disposition en croix et les significations des cartes entre elles.
             Les cartes fournies sont : {cards_list} il y a le mon et l'url de l'image de la carte pour generer la réponse.
            Voici comment lire un tirage en croix :
            - La première carte représente votre situation actuelle.
            - La deuxième carte montre les difficultés et obstacles potentiels.
            - La troisième carte symbolise les événements futurs proches.
            - La quatrième carte apporte une réponse ou un éclairage sur la situation.
            - La cinquième carte résume la situation et offre une synthèse.

            Les cartes sont fournies dans le contexte avec leur signification et leur position dans le tirage en croix. Si tu as d'autres informations sur les cartes, tu peux les ajouter pour améliorer la réponse.

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
        document_chain = create_stuff_documents_chain(model, prompt)
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        # Pose une question spécifique en fonction des cartes tirées
        question = input_value.get("question", "Quelle est ma prédiction ?")
        response = retrieval_chain.invoke(
            {
                "input": question,
                "context": full_text,
                "cards_list": cards,
            }
        )
        prediction = response.get("answer", "No prediction available.")

        # Use AIMessage to structure the response
        ai_message = AIMessage(content=prediction)

        # Vérifiez si la réponse est vide ou mal formée
        if not ai_message.content:
            raise ValueError("Empty response from the model")

        def extract_json(response_text):
            """Extrait la partie JSON valide de la réponse brute."""
            try:
                # Log de la réponse brute pour le débogage
                logger.debug("Réponse brute: %s", response_text)

                # Recherche du premier bloc JSON valide
                json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if json_match:
                    json_data = json_match.group()

                    # Supprimer les nouvelles lignes et les caractères supplémentaires
                    json_data = re.sub(r"\n", "", json_data)

                    # Validation du JSON
                    try:
                        parsed_data = json.loads(json_data)
                        return parsed_data
                    except json.JSONDecodeError as inner_error:
                        logger.error("Erreur de parsing JSON: %s", inner_error)
                        raise ValueError(f"Erreur de parsing JSON : {inner_error}")
                else:
                    raise ValueError("Aucun JSON valide trouvé.")
            except Exception as e:
                logger.error(f"Erreur générale dans l'extraction JSON: {e}")
                raise ValueError(f"Erreur générale : {str(e)}")

        response_dict = extract_json(ai_message.content)

        # Access keys and values
        for key, value in response_dict.items():
            print(f"{key}: {value}")

        return {
            "subject": "prediction",
            "predictions": [response_dict],
            "cards": cards,
        }

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"subject": "error", "message": str(e)}
