import requests
from bs4 import BeautifulSoup
#from langchain.document_loaders import WebBaseLoader
from langchain_community.document_loaders import WebBaseLoader
from bs4 import SoupStrainer
from threading import Thread
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from Blender_Agentic_RAG.data_extraction.utils import EmbeddingsSource,VectorDBSource,get_embedding,create_vdb

def extract_links(version,limit=None):
    if float(version) <= 4: print('Warning, this method works only for blender verson 4.1 or higher')
    base_url = f'https://docs.blender.org/manual/en/{version}/'

    response = requests.get(base_url)
    bs = BeautifulSoup(response.text,'lxml')

    side_bar = bs.find('div',{'class':'sidebar-tree'})
    bs_side_bar = BeautifulSoup(str(side_bar),'lxml')
    side_bar_items = bs_side_bar.find_all('a',limit=limit)

    links = {}
    for item in side_bar_items:
        link = item.get('href')
        if link and not link.endswith('index.html'):
            full_link = base_url + link
            if full_link not in links:
                links[full_link] = {'info':item.text,'version':version}

    print(f'Extracted {len(links)} urls')
    return links


def extract_docs(links:dict,n_jobs:int):
    keys = list(links.keys())
    values = list(links.values())

    threads = []
    results = [0]*len(links)
    n_jobs = n_jobs if n_jobs > 0 else os.cpu_count()
    for i in range(n_jobs):
        thread = Thread(target=worker, args=(keys,values,i,n_jobs,results ))
        threads.append(thread)
        thread.start()

    for p in threads:
        p.join()

    return [item for items in results for item in items ]


def worker(keys,values,start,inc,results):
    for i in range(start,len(keys),inc):
        web_loader = WebBaseLoader(keys[i],bs_kwargs=dict( parse_only=SoupStrainer('article') ) )
        docs = web_loader.load()
        for doc in docs:
            doc.metadata['info'] = values[i]['info']
            doc.metadata['version'] = values[i]['version'] #values[i]['version']
        results[i] = docs

def create_vector_db(version,path,embeddings_source:EmbeddingsSource,vectordb_source:VectorDBSource,model_name:str = 'nomic-embed-text',
                     chunk_size = 2000, chunk_overlap = 300,n_jobs=-1,links_limit=None):
    print(f'Extracting links for version {version}')
    links = extract_links(version,limit=links_limit)

    print(f'Extracting docs')
    docs = extract_docs(links,n_jobs=n_jobs)

    print(f'Spliting docs')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size,chunk_overlap = chunk_overlap)
    docs_split = text_splitter.split_documents(docs)

    print(f'Creating vectordb')
    embedding = get_embedding(embeddings_source,model_name)
    return create_vdb(path,docs_split,embedding,version,vectordb_source)


