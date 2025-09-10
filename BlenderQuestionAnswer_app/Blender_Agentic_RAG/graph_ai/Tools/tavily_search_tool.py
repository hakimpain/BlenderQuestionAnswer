
from langchain.tools import BaseTool
from langchain_tavily import TavilySearch
from langchain_core.documents import Document

class TavilySearchTool(BaseTool):
    max_results: int = 3
    include_answer: bool = False
    search_api : TavilySearch = TavilySearch(search_depth="advanced",include_raw_content=True)
    name: str = 'tavily_search_tool'
    version: str

    description: str =(
    "Search the internet\n"
    "Args:\n"
    "query: search text string for anything, make sure to include blender 3d software version {version} in the context"
    )

    def format_description(self,version=None):
        self.version = version if version else self.version
        self.description = self.description.format(version = self.version)

    def _run(self,query:str):
        self.search_api.max_results = self.max_results
        self.search_api.include_answer = self.include_answer
        res = self.search_api.invoke(query)
        docs = self.get_docs(res)
        return docs
        
    def get_docs(self, results):
        docs = []
        if 'answer' in results and results['answer'] is not None:
            docs.append(Document(results['answer']))
        for result in results['results']:
            doc = Document(result['content'],metadata={'title':result['title']})
            docs.append(doc)
        return docs