import os
import logging
import time
import json

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

        # Summarize each card's text
        cards_text = [
            MajorArcana.objects.get(card_name_fr=card).card_text()
            for card in cards_list
        ]
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
            voici comment liore une tirage en croix:
            Comment lire les cartes en croix ?
            Dans le tirage en croix, chaque carte a une place et une signification prédéfinie. Ainsi, il est important de bien les positionner selon l’ordre dans lesquelles on les tire. La première carte va tout à gauche. La seconde, tout à droite. En haut, ira la troisième carte, en bas, la quatrième. Et, enfin, au milieu, on retrouvera la dernière carte. Voici un modèle pour vous aider à vous repérer. 
            Tirage en croix : signification de la première carte
            La première carte représente votre situation. Elle met en lumière votre état d’esprit, votre personnalité, ce qui est en train de se passer au moment où vous tirez les cartes. Comment se présente la situation ? Quelle est la conjoncture ? Selon l’arcane qui sort, il peut s’agir de quelque chose de positif ou, au contraire, de plutôt négatif. Par chance, les prochaines cartes vous aideront à dénouer tout cela en vous donnant les clés nécessaires pour améliorer ou faire évoluer votre situation. En réalité, toutes les arcanes possèdent du positif ou du négatif. Tout dépend de leur place dans le tirage et de l’état d’esprit du consultant. Dans certains cas, la première carte d’un tirage en croix peut également représenter le consultant. 

            Tirage en croix : interprétation de la deuxième carte
            Après avoir posé les bases de la situation, il est important d’en comprendre les tenants et les aboutissants. La seconde carte est là pour vous montrer les difficultés, les aspects négatifs et les obstacles potentiels qui peuvent se présenter à vous. Par exemple, dans le cadre d’un tirage sentimental, il peut s’agir d’une carte qui nous parle de jalousie ou d’instabilité. Il faudra donc surmonter ce potentiel problème afin d’avancer, ou du moins, en tenir compte pour comprendre la situation dans son ensemble. Cela n’est pas forcément négatif. Il peut arriver qu’une carte lumineuse se présente à vous. Dans ce cas, le tirage vous révèle quels sont vos appuis, vos soutiens, les forces sur lesquelles travailler pour évoluer. Dans les deux cas, il s’agit d’une étape à passer pour transformer le présent. Rappelons que tout doit venir de vous. Cette carte est donc là pour vous montrer quelle part de votre personnalité est challenger dans cette situation. 

            Tirage en croix : que représente le troisième arcane ? 
            La troisième carte symbolise les évènements. Elle vous révèle votre futur proche. Que peut-il se passer qui risque de transformer votre situation, de changer votre quotidien. Attention, il ne faut pas s’attendre à de grands bouleversements, cela peut être quelque chose de discret comme un message que l’on reçoit ou une personne que l’on croise. Que l’arcane sélectionnée soit positive ou négative, dans les deux cas, elle vous invitera à vous ouvrir au monde. Restez attentive, observez, soyez prête à intercepter les signes de l’Univers. Bien souvent, il arrive que l’on ne se rende pas compte de ce qu’il se passe. On peut donc avoir l'impression que rien n’arrive alors qu’un événement a bien eu lieu. Pas de panique donc si dans les prochains jours, prochaines semaines ou même prochains mois, vous ne voyez rien. N’attendez rien, ne précipitez rien. Faites-vous seulement confiance.

            La signification de la quatrième carte dans un tirage en croix
            Vous avez posé une question concrète, mais pour l’instant aucune réponse n’arrivait. Les trois premières cartes sont des soutiens, des appuis pour comprendre la situation. Elles permettent de mettre au clair tout ce qui se passe dans votre vie pour vous permettre de réaliser pourquoi vous en êtes là. La quatrième carte est celle de la réponse. Enfin ! Elle vous apporte une solution, un éclairage sur ce qui risque de vous arriver, sur ce qui peut se passer. Mais attention. Un tirage du tarot de Marseille n’a rien de magique. Vous êtes et serez toujours la seule personne capable d’influencer votre destin. Ainsi, si les cartes vous disent que vous allez faire une rencontre et vivre une nouvelle histoire d’amour, l’impulsion ne peut venir que de vous. Il faut comprendre par là que si vous ne sortez pas de chez vous et que vous ne croisez personne, l’âme sœur ne tombera pas du ciel. Les cartes ne sont que des suppositions, elles vous proposent une alternative à votre futur à cet instant T. Tout peut changer et évoluer selon les décisions que vous prenez. Au même titre qu’elles vous prodiguent des conseils, mais que si vous décidez d’en faire abstraction, il peut que rien ne change. C’est aussi ça, le libre arbitre ! 

            La cinquième carte du tirage en croix
            La dernière carte du tirage en croix est une sorte de carte bonus. Elle résume la situation, vous dresse une synthèse de tout ce que les autres arcanes ont pu et su vous dire. Servez-vous en comme d’un bilan. Voici ce qui se présente à vous. Voilà quel est votre défi. Une fois de plus, il s’agit ici de faire une petite introspection. Quelles sont les choses que vous avez appris sur vous, sur votre combativité, sur vos désirs, vos envies ? Que retenez-vous de ce tirage ? La dernière carte vous renvoie face à votre propre image pour vous montrer que vous êtes la seule personne capable de transformer votre destin. Pourquoi la situation est-elle ainsi ? Quelles leçons, quels conseils, les cartes et ce tirage peuvent vous apprendre pour sortir grandie de tout cela ? On vous conseille de prendre votre temps pour bien prendre le temps d’analyser et d’interpréter le tirage. Sortez une feuille et un stylo et notez tout ce qui vous vient en tête. Quels messages apparaissent ? Écoutez votre intuition, restez au fait de vos émotions, de vos ressentis. Ce sont eux qui vous guideront vers la solution. 
            Tu dois fournir une réponse uniquement en JSON strictement valide sans texte ou annotation autour. Le format doit correspondre à cet exemple exact :

            {{
                "carte1": {{
                    "nom": "La Situation",
                    "signification": "Mise en lumière de l’état d’esprit et de la personnalité, représentant la conjoncture actuelle. Peut être positive ou négative selon l’arcane."
                }},
                "carte2": {{
                    "nom": "Les Difficultés",
                    "signification": "Révélation des aspects négatifs, des obstacles potentiels ou des soutiens, mettant en avant une part de la personnalité à challenger."
                }},
                "carte3": {{
                    "nom": "Les Événements",
                    "signification": "Symbolisation des événements à venir qui peuvent transformer la situation, invitant à rester attentif et ouvert au monde."
                }},
                "carte4": {{
                    "nom": "La Réponse",
                    "signification": "Apport d’une solution ou d’un éclairage sur ce qui risque de se passer, influencé par les décisions du consultant."
                }},
                "carte5": {{
                    "nom": "La Synthèse",
                    "signification": "Résumé de la situation et bilan pour guider le consultant face à son propre destin et ses propres choix."
                }},
                "prediction": "Une prédiction basée sur l’ensemble des cartes tirées, tenant compte de leur position et de leur signification.",
                "reponse": "Une réponse personnalisée basée sur la question posée et les cartes tirées."
            }}

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
        response = retrieval_chain.invoke({"input": question, "context": full_text})
        prediction = response.get("answer", "No prediction available.")

        # Use AIMessage to structure the response
        ai_message = AIMessage(content=prediction)

        # Vérifiez si la réponse est vide ou mal formée
        if not ai_message.content:
            raise ValueError("Empty response from the model")

        ai_message_escape = ai_message.content.replace("\\", "")
        # Parse the JSON response
        try:
            response_dict = json.loads(ai_message_escape)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError("Invalid JSON response from the model") from e

        # Access keys and values
        for key, value in response_dict.items():
            print(f"{key}: {value}")

        return {
            "subject": "prediction",
            "predictions": [ai_message.content],
            "cards": cards,
        }

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"subject": "error", "message": str(e)}
