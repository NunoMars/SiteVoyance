import os
import PyPDF2
from langchain.embeddings import MistralEmbeddings
import faiss
import numpy as np
from dotenv import load_dotenv


load_dotenv()


# Étape 1 : Lire le fichier PDF et extraire le texte
def extract_text_from_pdf(pdf_path):
    pdf_reader = PyPDF2.PdfFileReader(open(pdf_path, "rb"))
    text = ""
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        text += page.extract_text()
    return text


# Étape 2 : Utiliser LangChain pour transformer le texte en vecteurs
def text_to_vectors(text, api_key):
    embeddings = MistralEmbeddings(api_key=api_key)
    return embeddings.embed_text(text)


# Étape 3 : Indexer les vecteurs avec FAISS
def index_vectors(vectors):
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)
    return index


# Chemin vers le fichier PDF
pdf_path = "TarotModeEmploi.pdf"

# Votre clé API Mistral
api_key = os.getenv("MISTRAL_API_KEY")

# Extraire le texte du PDF
text = extract_text_from_pdf(pdf_path)

# Convertir le texte en vecteurs
vectors = text_to_vectors(text, api_key)

# Indexer les vecteurs avec FAISS
index = index_vectors(np.array(vectors))

print("Indexation terminée.")
