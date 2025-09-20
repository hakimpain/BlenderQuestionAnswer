from enum import Enum
from langchain_core.messages import AIMessage,BaseMessage
from langchain_core.documents import Document
from typing import TypedDict

from Blender_Agentic_RAG.graph_ai.AI_Memory.ai_memory import get_temp_ai_memory,MemoryType

class SearchState(Enum):
    FIRST_SEARCH=0
    REWRITE_SEARCH=1
    EXTERNAL_SEARCH=2
    END_SEARCH = 3

    def get_next_state(self,allow_external_search):
        inc = 1 if self.value < SearchState.END_SEARCH.value else 0
        next_state = SearchState(self.value+inc)
        if not allow_external_search and next_state == SearchState.EXTERNAL_SEARCH:
            return SearchState.END_SEARCH
        return next_state

class State(TypedDict):
    question:str
    search_query:AIMessage #class that contains the tool calls list
    search_result:list[Document]
    answer:str
    suggestions:str
    search_state:SearchState
    allow_external_search:bool
    session_id:int
    ai_memory:list[BaseMessage]
    memory_type:MemoryType
    state_name:str #Debugging only with straming...

def get_initial_state(question,session_id,search_state=SearchState.FIRST_SEARCH,allow_external_search = False,memory_type=MemoryType.TEMPORARY,ai_memory=None):
    
    if memory_type == MemoryType.TEMPORARY:
        ai_memory = get_temp_ai_memory(session_id).copy()

    if isinstance(ai_memory,list) and len(ai_memory) > 5: #trim memory
        ai_memory = ai_memory[-5:]

    return {
        'question':question,
        'session_id':session_id if memory_type != MemoryType.DISABLED else None,
        'search_state':search_state,
        'ai_memory': ai_memory,
        'allow_external_search':allow_external_search,
        'memory_type':memory_type
    }