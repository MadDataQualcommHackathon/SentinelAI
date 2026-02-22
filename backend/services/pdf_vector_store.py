import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class PDFVectorStore:
    def __init__(self, persist_directory="./cuad_chroma_db"):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.persist_directory = persist_directory

    def build_from_directory(self, directory_path):
        print(f"--- Loading PDFs from {directory_path} ---")
        loader = PyPDFDirectoryLoader(directory_path)
        raw_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, 
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunked_docs = text_splitter.split_documents(raw_documents)
        print(f"--- Split {len(raw_documents)} pages into {len(chunked_docs)} chunks ---")

        vector_db = Chroma.from_documents(
            documents=chunked_docs,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return vector_db