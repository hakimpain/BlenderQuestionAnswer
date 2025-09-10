
from Blender_Agentic_RAG.graph_ai.LLMs.llms import LLMs,LLMSources
from Blender_Agentic_RAG.graph_ai.States.states import State,get_initial_state,SearchState,MemoryType
from Blender_Agentic_RAG.graph_ai.Nodes.conditions import NodeConditions
from Blender_Agentic_RAG.graph_ai.Nodes.nodes import Nodes
from Blender_Agentic_RAG.graph_ai.Tools.tools_main import MainTools
from Blender_Agentic_RAG.data_extraction.main_data_extraction import get_vector_db_retriever,EmbeddingsSource,VectorDBSource
from Blender_Agentic_RAG.graph_ai.AI_Memory.ai_memory import save_ai_memory

from langgraph.graph import StateGraph,START,END

class AgenticGraph:
    def __init__(self,
                 blender_version = '4.5',
                 main_model: str = 'llama3.1:8b',
                 source: LLMSources = LLMSources.OLLAMA,
                 deterministic_model = None,
                 recom_model = None,
                 creative_model = None,
                 include_tavily_answer=False,
                 max_tavily_results=3,
                 n_results_vdb = 4,
                 search_variation_vdb = 0.9,
                 vdbs_path = '',
                 embeddings_source = EmbeddingsSource.OLLAMA,
                 vectordb_source = VectorDBSource.FAISS,
                 embedding_name = 'nomic-embed-text'
                 ):
        
        self.busy = False
        self.version = blender_version
                
        llms = LLMs(main_model=main_model,source=source,deterministic_model=deterministic_model,
                    recom_model=recom_model,creative_model=creative_model)
        
        vdb_retriever = get_vector_db_retriever(version=blender_version,
                                                path=vdbs_path,
                                                embeddings_source=embeddings_source,
                                                vectordb_source =vectordb_source,
                                                model_name = embedding_name,
                                                n_results = n_results_vdb,
                                                search_variation = search_variation_vdb)
        
        main_tools = MainTools(llms.llm_creative,
                               vdb_retriever=vdb_retriever,
                               version=blender_version,
                               tavily_max_results=max_tavily_results,
                               tavily_include_answer=include_tavily_answer)
        
        llms.setup_llms_with_tools(main_tools=main_tools)

        nodes = Nodes(llms=llms,main_tools=main_tools)
        nodes_conditions = NodeConditions(llms=llms)


        graph = StateGraph(State)

        graph.add_node('out_of_context_node',nodes.out_of_context_node)
        graph.add_node('tool_choice_node',nodes.tool_choice_node)
        graph.add_node('retriever',nodes.retrieve_call_node)
        graph.add_node('rewrite_node',nodes.rewrite_node)
        graph.add_node('answer_node',nodes.answer_node)
        graph.add_node('recomendations_node',nodes.recomendations_node)

        graph.add_conditional_edges(START,
                                    nodes_conditions.check_context_condition,
                                    {
                                        'Out of context':'out_of_context_node',
                                        'Valid context':'tool_choice_node'
                                    })

        graph.add_conditional_edges('tool_choice_node',
                                    nodes_conditions.retrieve_query_condition,
                                    {
                                        'retriever':'retriever',
                                        'recommendation':'recomendations_node'
                                    })

        graph.add_conditional_edges('retriever',
                                    nodes_conditions.rewrite_search_condition,
                                    {
                                        'Generate':'answer_node',
                                        'Rewrite': 'rewrite_node'
                                    }
                                    )

        graph.add_edge('rewrite_node','tool_choice_node')
        graph.add_edge('answer_node','recomendations_node')
        graph.add_edge('recomendations_node',END)
        graph.add_edge('out_of_context_node',END)
        #graph.add_edge('retriever','answer_node')

        self.graph = graph.compile()
    
    def invoke(self,question, session_id, search_state: SearchState = SearchState.FIRST_SEARCH, allow_external_search: bool = False,
               memory_type: MemoryType = MemoryType.TEMPORARY, ai_memory = None, stream_mode = None):
        
        self.busy = True

        initial_state = get_initial_state(question=question,
                                          session_id=session_id,
                                          search_state=search_state,
                                          allow_external_search=allow_external_search,
                                          memory_type=memory_type,
                                          ai_memory=ai_memory)
        
        if stream_mode and (stream_mode == 'updates' or stream_mode == 'values'):
            response = []
            for event in self.graph.stream(initial_state,stream_mode=stream_mode):
                response.append(event)
        else:
            response = self.graph.invoke(initial_state)
        
        save_ai_memory(response[-1] if isinstance(response,list) else response)

        self.busy = False

        return response

    
