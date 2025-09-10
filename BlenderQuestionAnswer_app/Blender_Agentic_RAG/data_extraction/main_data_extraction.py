

from Blender_Agentic_RAG.data_extraction.create_vectordb_4_1_to_5_0 import create_vector_db as create_vector_db_4_1_to_5
from Blender_Agentic_RAG.data_extraction.utils import EmbeddingsSource,VectorDBSource,get_embedding,get_vdb

def create_vector_db(version,path,embeddings_source:EmbeddingsSource,vectordb_source:VectorDBSource,model_name:str = 'nomic-embed-text',
                     chunk_size = 2000, chunk_overlap = 300, n_jobs = -1, links_limit = None):
    try:
        version_float = float(version)
    except:
        raise ValueError('Invalid version value')
    
    if version_float >= 4.1 and version_float <= 5.0:
        return create_vector_db_4_1_to_5(version,path,embeddings_source,vectordb_source,model_name,chunk_size,chunk_overlap,n_jobs,links_limit)

    raise ValueError('Unsuported blender version value')

def get_vector_db_retriever(version,path,embeddings_source:EmbeddingsSource,vectordb_source:VectorDBSource,model_name:str = 'nomic-embed-text',
                  n_results = 4,search_variation = 0.9):
    embedding = get_embedding(embeddings_source,model_name)
    vectordb = get_vdb(path,version,embedding,vectordb_source)
    return vectordb.as_retriever(search_type="mmr",search_kwargs={'k': n_results, 'lambda_mult': search_variation})

