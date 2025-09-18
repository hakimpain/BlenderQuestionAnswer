
from pydantic import BaseModel,Field
from typing import Literal #Annotated
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from enum import Enum
from Blender_Agentic_RAG.graph_ai.Tools.tools_main import MainTools

class ContextNodeStruct(BaseModel):
    answer:Literal['yes','no'] = Field(description='Answer if the question is relevant with yes or no')
    #answer:Annotated[Literal['yes','no'],'Answer if the question is relevant with yes or no']

class QuestionStructure(BaseModel):
    new_question:str = Field(description='New rewritten question')
    #new_question:Annotated[str,'New rewritten question']

class LLMSources(Enum):
    GROQ=0
    OLLAMA=1

class LLMs:
    def __init__(self,main_model = 'llama3.1:8b',source = LLMSources.OLLAMA, deterministic_model = None, recom_model = None, creative_model = None):
        self.setup_llm_models(main_model,source,deterministic_model, recom_model, creative_model)

    def setup_llm_models(self,main_model,source,deterministic_model, recom_model, creative_model):
        self.source = source
        self.deterministic_model = deterministic_model if deterministic_model else main_model
        self.recom_model = recom_model if recom_model else main_model
        self.creative_model = creative_model if creative_model else main_model

        self.llm = self.get_model(main_model,temperature=None)
        self.llm_deterministic = self.get_model(self.deterministic_model,temperature=0)
        self.llm_recommendations = self.get_model(self.recom_model,temperature=1.0)
        self.llm_creative = self.get_model(self.creative_model,temperature=1.0)

        self.llm_context_struct = self.llm_deterministic.with_structured_output(ContextNodeStruct)
        self.llm_new_question_struct = self.llm_creative.with_structured_output(QuestionStructure)
    
    def setup_llms_with_tools(self,main_tools:MainTools,):
        self.llm_vdb_tools = self.llm.bind_tools( main_tools.get_initial_state_tools() )
        self.llm_external_tools = self.llm.bind_tools( main_tools.get_final_state_tools() )

    def get_model(self,model,temperature=None):
        if self.source == LLMSources.GROQ:
            return ChatGroq(model=model,temperature=temperature)
        elif self.source == LLMSources.OLLAMA:
            from Blender_Agentic_RAG.graph_ai.graph_settings import ollama_base_url
            return ChatOllama(base_url=ollama_base_url,model=model,temperature=temperature)