import os
import PyPDF2
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
import faiss
import numpy as np
from dotenv import load_dotenv


load_dotenv()


class CreateVectors:
    """ Cretes vectors from a PDF file"""
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def extract_text_from_pdf(self):
        pdf_reader = PyPDF2.PdfReader(open(self.pdf_path, "rb"))
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text

    def text_to_vectors(self, text):
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return embeddings.embed_text(text)

    def index_vectors(self, vectors):
        dimension = vectors.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(vectors)
        return index

    def create_index(self):
        text = self.extract_text_from_pdf()
        vectors = self.text_to_vectors(text)
        index = self.index_vectors(np.array(vectors))
        print("indexation terminée.")      
        return index
