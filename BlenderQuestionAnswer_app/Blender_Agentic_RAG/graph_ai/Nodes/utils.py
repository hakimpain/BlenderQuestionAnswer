
import re
from Blender_Agentic_RAG.graph_ai.States.states import State

def docs_to_str(docs):
    docs_strings = []
    for doc in docs:
        page_content = doc.page_content
        docs_strings.append( re.sub(r'(\s)+',r'\1',page_content) )
    return '\n\n'.join(docs_strings)

#dont directly save new question since it may be rewritten by the ai
def get_memory_str(state:State):
    if state['ai_memory'] is None or len(state['ai_memory']) == 0:
        return f"Given the user question:\n{state['question']}"

    historic = state['ai_memory']
    introduction = "Given the previous questions and answers historic:\n"
    
    historic = '\n'.join([f"###Question\n{msg['question']}\n###Answer\n{msg['answer']}\n{msg['suggestions']}" for msg in historic])

    new_question = '\n###New question (in context with the previous messages)\n'+state['question']
    return introduction + historic + new_question