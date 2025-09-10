
from .models import VectordbBlenderDocs

def get_available_versions():
    all_vdbs = VectordbBlenderDocs.objects.all()
    return [vdb.version for vdb in all_vdbs]