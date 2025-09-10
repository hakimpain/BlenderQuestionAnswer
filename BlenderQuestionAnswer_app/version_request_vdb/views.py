from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib import messages

from .models import VectordbBlenderDocs

from Blender_Agentic_RAG.data_extraction.main_data_extraction import create_vector_db

from .utils import get_available_versions
# Create your views here.

tasks = []

def version_request(request):
    versions = [ v for v in settings.SUPORTED_VERSIONS if v not in get_available_versions() ]
    return render(request,'version_request.html',{'available_versions':versions})

def request_version_vdb(request):
    response = {}
    if request.method == 'POST' and 'version' in request.POST:

        version = request.POST['version']
        if version in tasks:
            return JsonResponse({'msg':'This version has already been requested and should be available in a few minutes...'})

        if version in get_available_versions():
            return JsonResponse({'msg':'Version already available'})
        
        tasks.append(version)

        res = create_vector_db(version = version,
                    path = settings.VECTOR_DATABASES_DIR,
                    embeddings_source = settings.EMBEDDING_SOURCE,
                    vectordb_source = settings.VECTORDB_SOURCE,
                    model_name = settings.EMBEDDING_MODEL_NAME,
                    chunk_size = 2000, 
                    chunk_overlap = 300,
                    n_jobs = -1,
                    links_limit = None)
        
        if res:
            VectordbBlenderDocs.objects.create(path = settings.VECTOR_DATABASES_DIR,
                                               version = version,
                                               embedding_model_name = settings.EMBEDDING_MODEL_NAME,
                                               embedding_source = settings.EMBEDDING_SOURCE.value[0],
                                               vector_db_source = settings.VECTORDB_SOURCE.value[0])
            response = {'msg':'Blender version documentation successfully added!'}
        else:
            response = {'msg':'Failed to add the new version'}

        tasks.remove(version)

    return JsonResponse(response)