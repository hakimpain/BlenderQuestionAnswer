
from enum import Enum
from langchain_ollama import OllamaEmbeddings
#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
import os

#Currently supports only ollama and FAISS vdb
class EmbeddingsSource(Enum):
    OLLAMA = 0
    HUGGING_FACE = 1
    OPEN_AI = 2

class VectorDBSource(Enum):
    FAISS = 0
    CHROMA = 1
    ASTRA_DB = 2
    PINECONE = 3


def get_embedding(embeddings_source:EmbeddingsSource,moel_name:str):
    if embeddings_source == EmbeddingsSource.OLLAMA:
        from Blender_Agentic_RAG.graph_ai.graph_settings import ollama_base_url
        return OllamaEmbeddings(base_url=ollama_base_url,model=moel_name)
    
    raise ValueError('Unsuported embeddings source')

def create_vdb(path,docs,embedding,version,vectordb_source:VectorDBSource):
    try:
        if vectordb_source == VectorDBSource.FAISS:
            vectorstore = FAISS.from_documents(docs,embedding=embedding)
            vectorstore.save_local( os.path.join(path,f'vectordb_{version}') )
            return True
    except Exception as e:
        print(e)
        return False

    raise ValueError('Unsuported vector database source')

def get_vdb(path,version,embedding,vectordb_source:VectorDBSource):
    if vectordb_source == VectorDBSource.FAISS:
        return FAISS.load_local( os.path.join(path,f'vectordb_{version}'),embedding,allow_dangerous_deserialization=True)
    
    raise ValueError('Unsuported vector database source')
