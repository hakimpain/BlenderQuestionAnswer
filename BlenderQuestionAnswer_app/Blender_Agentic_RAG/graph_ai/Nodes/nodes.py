from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from Blender_Agentic_RAG.graph_ai.States.states import State,SearchState
from Blender_Agentic_RAG.graph_ai.LLMs.llms import LLMs
from Blender_Agentic_RAG.graph_ai.Tools.tools_main import MainTools
from Blender_Agentic_RAG.graph_ai.Nodes.utils import docs_to_str,get_memory_str

from langchain_core.messages import HumanMessage,AIMessage,SystemMessage

class Nodes:
    def __init__(self,llms:LLMs,main_tools:MainTools):
        self.llms = llms
        self.main_tools = main_tools

    def out_of_context_node(self,state:State):
        return {'answer':'The question does\'t seems to be related to Blender 3D software. Please make sure to write a consist Blender question.',
                'state_name':'out_of_context_node'}

    
    def tool_choice_node(self,state:State):
        #Give different tools to the llm depending on the search state
        search_state = state['search_state']
        response = None
        if search_state.value <= SearchState.REWRITE_SEARCH.value:
            response = self.llms.llm_vdb_tools.invoke( get_memory_str(state) )
        elif search_state == SearchState.EXTERNAL_SEARCH and state['allow_external_search']:
            response = self.llms.llm_external_tools.invoke( get_memory_str(state) )
        return {'search_query':response,'search_state':search_state.get_next_state(state['allow_external_search']),
                'state_name':'tool_choice_node'}

    def retrieve_call_node(self,state:State):
        results = []
        for search_query in state['search_query'].tool_calls:
            for tool in self.main_tools.get_all_tools():
                if tool.name == search_query['name']:
                        try:
                            res = tool.invoke(search_query['args'])
                            results.extend(res)
                        except Exception as e:
                            print(f"Tool {tool.name} call failed for args {search_query['args']}\n{e}")
                            results.append(Document(page_content='Search failed...'))
                
        return {'search_result':results,'state_name':'retrieve_call_node'}


    def rewrite_node(self,state:State):
        msgs = [
            SystemMessage((
            "The latest user question should be related to Blender 3D software. "
            "Check for semantic intent, meaning and misspelling to formulate an improved question.\n"
            "Always answer only the new improved question."
            )),
            *get_memory_str(state)
        ]
        return {'question': self.llms.llm_new_question_struct.invoke(msgs).new_question,'state_name':'rewrite_node'}
        # prompt_str = ("{conversation}\n"
        #             "The new question should be related to Blender 3D software. "
        #             "Check for semantic intent, meaning and misspelling to formulate an improved question.\n"
        #             "Always answer only the new improved question.")
        # prompt = PromptTemplate(template=prompt_str,input_variables=['conversation'])
        # chain = prompt | self.llms.llm_new_question_struct | RunnableLambda(lambda x: x.new_question) #| StrOutputParser()
        # return {'question': chain.invoke({'conversation':get_memory_str(state)}),
        #         'state_name':'rewrite_node'}

    def answer_node(self,state:State):
        msgs = [
            SystemMessage((
                        "Using only the following context:\n"
                        f"{docs_to_str(state['search_result'])}"
                        "Answer the new user question."
            )),
            *get_memory_str(state)
        ]

        chain = self.llms.llm | StrOutputParser()
        response = chain.invoke( msgs )
        return {'answer':response,'state_name':'answer_node'}
        # prompt_str = (
        # "{conversation}\n"
        # "Using only the following context:\n"
        # "{context}"
        # "Answer the new user question:\n"
        # )
        # prompt = PromptTemplate(input_variables=['context','question'],template=prompt_str)

        # chain = prompt | self.llms.llm | StrOutputParser()
        # response = chain.invoke( {'context':docs_to_str(state['search_result']),'conversation':get_memory_str(state)} )
        # return {'answer':response,'state_name':'answer_node'}


    def recomendations_node(self,state:State):
        msgs = [
            SystemMessage((
                'Answer recommendations based on the following conversation that the user may be interested to search. '
                'Make sure to stay in the context of the Blender 3D software.\n'
                'Answer only short enumareted suggestions related with the latest context of the conversation.\n'
                'The maximun suggestions should be 3.'
                )),
                *get_memory_str(state)
        ]
        if 'answer' in state:
            msgs.append(AIMessage(state['answer']))
            msgs.append(HumanMessage('Answer recommendations.'))
        else: msgs.append(HumanMessage('Answer recommendations and possible corrections.'))
        
        chain = self.llms.llm_recommendations | StrOutputParser()
        return {'suggestions':chain.invoke(msgs),'state_name':'recomendations_node'}
    
        # if 'answer' in state:
        #     prompt_str = ("{conversation}\n"
        #     "answer: {answer}\n"
        #     "Answer short related questions or ideas that the user may be interested to search.\n").format(conversation=get_memory_str(state),
        #                                                                                         answer=state['answer'])
        # else:
        #     prompt_str = ("{conversation}\n"
        #     "Answer short related suggestions or corrections that the user may be interested to search.\n").format(conversation=get_memory_str(state))
        
        # prompt_str += ("Make sure to stay in the context of the Blender 3D software.\n"
        #             "Answer only enumareted suggestions WITHOUT answers, the maximun suggestions should be 3.")
        # chain = self.llms.llm_recommendations | StrOutputParser()
        # return {'suggestions':chain.invoke( [HumanMessage(prompt_str)] ), 
        #         'state_name':'recomendations_node'}