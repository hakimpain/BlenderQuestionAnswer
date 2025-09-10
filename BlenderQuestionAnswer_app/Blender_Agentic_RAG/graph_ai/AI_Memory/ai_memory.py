
from enum import Enum

temp_memory = {}

class MemoryType(Enum):
    DISABLED=0
    TEMPORARY=1
    DATA_BASE=2

def get_temp_ai_memory(session_id):
    global temp_memory
    if session_id not in temp_memory:
        temp_memory[session_id] = []
    return temp_memory[session_id].copy()

def get_data_to_save(state):
    if state['memory_type'] != MemoryType.DISABLED and 'suggestions' in state:
        answer = state['answer'] if 'answer' in state else ''
        suggestion = state['suggestions']
        return {'question':state['question'],'answer':answer,'suggestions':suggestion} 
    return None

def save_ai_memory(state):
    new_message = get_data_to_save(state)
    if state['memory_type'] == MemoryType.TEMPORARY and new_message:
        get_temp_ai_memory( state['session_id'] ).append( new_message )
    #DATA_BASE mode will be stored on django view, could also use SQLChatMessageHistory from langchain


def clean_memory(session_id):
    global temp_memory
    if session_id in temp_memory:
        del temp_memory[session_id]
