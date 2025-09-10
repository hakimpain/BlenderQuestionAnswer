
from langchain.tools import BaseTool
from langchain_core.retrievers import BaseRetriever

class VectorDbSearch(BaseTool):
    name: str = 'vectordb_search_tool'
    description: str = ('Search on blender 3D software documentation\n'
    'Args:\n'
    'query: search text string, make sure use the exact blender tools names and keywords for better search.')

    vecdb_retriever: BaseRetriever

    def _run(self,query:str):
        return self.vecdb_retriever.invoke(query)