from django.http import JsonResponse
from .models import ChatMessage, ChatSession

from dotenv import load_dotenv
load_dotenv('C:/env/.env')

from Blender_Agentic_RAG.graph_ai.AI_Memory.ai_memory import MemoryType, get_data_to_save,clean_memory
from Blender_Agentic_RAG.graph_ai.States.states import SearchState
from Blender_Agentic_RAG.graph_ai.agentic_main import AgenticGraph

from .utils import generate_annonymous_session_key,get_graph,get_ai_memory

graphs : list[AgenticGraph] = []
annonymous_session_ids = []

def get_answer(request):
    print('--REQUEST--',request.POST)
    data = {}
    if request.method == 'POST' and 'question' in request.POST:
        question = request.POST['question']
        version = request.POST['version']
        use_memory = request.POST['use_memory'] == 'true'

        ai_memory = None
        session_id = None

        if not use_memory:
            memory_type = MemoryType.DISABLED
        elif request.user.is_authenticated:
            memory_type = MemoryType.DATA_BASE
            session_inst,ai_memory = get_ai_memory(version,request.user)
        else:
            memory_type = MemoryType.TEMPORARY
            if 'session_id' not in request.POST:
                session_id = generate_annonymous_session_key(annonymous_session_ids)
            else:
                session_id = request.POST['session_id']

        agentic_graph = get_graph(version=version,graphs=graphs)

        if agentic_graph is None:
            return JsonResponse({'error':'Version not available'})

        response = agentic_graph.invoke(
                    question = question, 
                    session_id = session_id, 
                    search_state = SearchState.FIRST_SEARCH, 
                    allow_external_search = True,
                    memory_type = memory_type, 
                    ai_memory = ai_memory,
                    stream_mode = None
                    )
        
        if memory_type == MemoryType.DATA_BASE:
            new_data = get_data_to_save(response)
            if new_data:
                ChatMessage.objects.create(
                    user_id = request.user,
                    chat_session = session_inst,
                    question = new_data['question'],
                    answer = new_data['answer'],
                    suggestion = new_data['suggestions'])

        if 'answer' in response:
            data['answer'] = response['answer']
        if 'suggestions' in response:
            data['suggestions'] = response['suggestions']
        if session_id is not None:
            data['session_id'] = session_id
    return JsonResponse(data)


def load_chat_history(request,version):
    if request.user.is_authenticated:
        session_messages = ChatMessage.objects.filter(chat_session=version,user_id=request.user)
        msgs = [msg_obj.get_data_for_history() for msg_obj in session_messages]
        return JsonResponse(msgs,safe=False)
    
    return JsonResponse({})

def clean_chat_history(request):
    msg = {}
    if request.method == 'POST':
        if 'session_id' in request.POST:
            clean_memory(request.POST['session_id'])
            msg = {'msg':'Successfully deleted all history'}
        if request.user.is_authenticated and 'version' in request.POST:
             version = request.POST['version']
             
             try:
                 chat_session = ChatSession.objects.get(version = version)
             except:
                 return JsonResponse({'msg':'Failed to remove history'})

             msgs = ChatMessage.objects.filter(chat_session=chat_session,user_id=request.user)
             n = len(msgs)
             msgs.delete()
             return JsonResponse({'msg':f'Successfuly deleted {n} messages history from version {version}'})
        
    return JsonResponse(msg)