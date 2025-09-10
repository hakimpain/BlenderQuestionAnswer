
from Blender_Agentic_RAG.graph_ai.Tools.creative_search_tool import CreativeTool
from Blender_Agentic_RAG.graph_ai.Tools.tavily_search_tool import TavilySearchTool
from Blender_Agentic_RAG.graph_ai.Tools.vectordb_tool import VectorDbSearch


class MainTools:
    def __init__(self,llm_creative,vdb_retriever,version,tavily_max_results=3,tavily_include_answer=False):
        self.creative_tool = CreativeTool(llm_creative=llm_creative,version=version)

        self.tavily_tool = TavilySearchTool(max_results=tavily_max_results,include_answer=tavily_include_answer,version=version)
        self.tavily_tool.format_description()

        self.vector_db_tool = VectorDbSearch(vecdb_retriever=vdb_retriever)

    def get_all_tools(self):
        return [self.creative_tool,self.tavily_tool,self.vector_db_tool]

    def get_initial_state_tools(self):
        return [self.creative_tool,self.vector_db_tool]

    def get_final_state_tools(self):
        return [self.tavily_tool]
    
    def update_version(self,vdb_retriever,version):
        self.vector_db_tool.vecdb_retriever = vdb_retriever
        self.creative_tool.version = version
        self.tavily_tool.format_description(version=version)
    