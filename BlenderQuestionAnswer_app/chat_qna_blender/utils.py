
from django.conf import settings
from django.core.management.utils import get_random_secret_key

from Blender_Agentic_RAG.data_extraction.utils import EmbeddingsSource, VectorDBSource
from Blender_Agentic_RAG.graph_ai.LLMs.llms import LLMSources
from Blender_Agentic_RAG.graph_ai.agentic_main import AgenticGraph
from chat_qna_blender.models import ChatMessage, ChatSession

from version_request_vdb.models import VectordbBlenderDocs


def generate_annonymous_session_key(annonymous_session_ids):
    new_key = get_random_secret_key()
    while new_key in annonymous_session_ids:
        new_key = get_random_secret_key()
    annonymous_session_ids.append(new_key)
    return new_key


def get_graph(version,graphs : list[AgenticGraph]):
    for graph in graphs:
        if not graph.busy and graph.version == version:
            return graph
    
    vector_db_info = VectordbBlenderDocs.objects.filter(version=version).order_by('-created_at')
    if len(vector_db_info) == 0:
        return None
    
    vector_db_info = vector_db_info[0]

    agentic_graph = AgenticGraph(blender_version = vector_db_info.version,
                                main_model = 'llama3.2:3b',#llama3.1:8b
                                source = LLMSources.OLLAMA,
                                deterministic_model = None,
                                recom_model = None,
                                creative_model = None,
                                include_tavily_answer=False,
                                max_tavily_results=3,
                                n_results_vdb = 4,
                                search_variation_vdb = 0.9,
                                vdbs_path = vector_db_info.path,
                                embeddings_source = EmbeddingsSource(vector_db_info.embedding_source),
                                vectordb_source = VectorDBSource(vector_db_info.vector_db_source),
                                embedding_name = vector_db_info.embedding_model_name)
    
    graphs.append(agentic_graph)
    return agentic_graph

def get_ai_memory(version,user):
    session = ChatSession.objects.filter(version=version)
    if len(session) == 0:
        session = ChatSession.objects.create(version=version)
        return session,[]
    
    ai_memory_objects = ChatMessage.objects.filter(user_id=user,chat_session=version).order_by('created_at')
    return session[0],[ memory_object.get_data_for_history() for memory_object in ai_memory_objects ]