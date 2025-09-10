
from typing import Literal
from langchain.prompts import PromptTemplate

from Blender_Agentic_RAG.graph_ai.States.states import State
from Blender_Agentic_RAG.graph_ai.LLMs.llms import LLMs
from Blender_Agentic_RAG.graph_ai.Nodes.utils import docs_to_str,get_memory_str

class NodeConditions:

    def __init__(self,llms:LLMs):
        self.llms=llms

    def check_context_condition(self,state:State) -> Literal['Out of context','Valid context']:
        prompt_msg = (
            "{conversation}\n\n"
            "Answer if the new question is related to the Blender 3D software.\n"
            "Answer only yes or no.")
            
        prompt_template = PromptTemplate(input_variables=['conversation'],template=prompt_msg)
        chain = prompt_template | self.llms.llm_context_struct

        res = chain.invoke( {'conversation':get_memory_str(state)} )
        return 'Valid context' if res.answer == 'yes' else 'Out of context'


    def retrieve_query_condition(self,state:State) -> Literal['retriever','recommendation']:
        search_query = state['search_query']
        return 'retriever' if hasattr(search_query,'tool_calls') and len(search_query.tool_calls) > 0 else 'recommendation'

    def rewrite_search_condition(self,state:State) -> Literal['Generate','Rewrite']:
        prompt_str = ("{conversation}\n"
        "Answer only yes or no if the answer of the new question can be found in the following context:\n{context}\n")
        prompt = PromptTemplate(input_variables=['conversation','context'],template=prompt_str)
        chain = prompt | self.llms.llm_context_struct
            
        response = chain.invoke( {'conversation':get_memory_str(state),'context':docs_to_str(state['search_result']) } ).answer

        return 'Generate' if response == 'yes' else 'Rewrite'