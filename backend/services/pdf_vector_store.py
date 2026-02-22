import chromadb
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_HOST = "localhost"
CHROMA_PORT = 8001
COLLECTION_NAME = "cuad_contracts"


class PDFVectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

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
            client=self.client,
            collection_name=COLLECTION_NAME,
        )
        print(f"--- Stored {len(chunked_docs)} chunks in ChromaDB at {CHROMA_HOST}:{CHROMA_PORT} ---")
        return vector_db

    def as_retriever(self, **kwargs):
        vector_db = Chroma(
            client=self.client,
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
        )
        return vector_db.as_retriever(**kwargs)
