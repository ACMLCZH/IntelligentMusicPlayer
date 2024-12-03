import uuid
from elasticsearch import Elasticsearch
es = Elasticsearch(["http://localhost:9200"])
from myapp.models import Song


def add_music(song: Song):
    '''
        add a music to Server Track Database.
    '''

    doc = dict(
        id=song.id,
        name=song.name,
        author=song.author,
        album=song.album,
        duration=song.duration,
        lyrics=song.lyrics,
        topics=song.topics,
        mp3_url=song.mp3_url,
        cover_url=song.cover_url,
    )
    es.index(index='music', body=doc)

    # index_name = 'music' # 使用 match_all 查询获取所有文档 
    # query = { "query": { "match_all": {} } } 
    # response = es.search(index=index_name, body=query, size=1000)
    # hits = response['hits']['hits'] 
    # for hit in hits: 
    #     print(hit['_source'])

    # songs = Songs.objects.all()
    # for song in songs: 
    #     print(f"ID: {song.id}, Name: {song.name}, Author: {song.author}, Duration: {song.duration}, Lyrics: {song.lyrics}, URL: {song.url}")


def delete_music(song: Song):
    '''
        delete a music from Server Track Database.
    '''

    # 查找文档ID
    query = {
        "query": {
            "match": {
                "name": song.name
            }
        }
    }
    response = es.search(index='music', body=query)
    doc_id = response['hits']['hits'][0]['_id']

    # 删除文档
    es.delete(index='music', id=doc_id)

    print("!!!!delete success!!!!")
    # print("!!!!current all index:!!!!")
    # index_name = 'music' # 使用 match_all 查询获取所有文档 
    # query = { "query": { "match_all": {} } } 
    # response = es.search(index=index_name, body=query, size=1000)
    # hits = response['hits']['hits'] 
    # for hit in hits: 
    #     print(hit['_source'])

def clear_es_database():
    '''
        Clear all documents from the specified Elasticsearch index.
    '''

    # Delete all documents in the index
    es.indices.delete(index='_all')

    print("!!!!index cleared!!!!")



def search_music(keyword: str, criteria: str, from_: int, size: int):
    '''
    search music in Server Track Database.
    '''

    if criteria == 'all':
        query = {
            "multi_match": {
                "query": keyword,
                "fields": ["id", "name", "author", "lyrics"]
            }
        }
    else:
        query = {
            "term": {
                criteria: keyword
            }
        }
    response = es.search(index='music', query=query, from_=from_, size=size)
    hits_total = response['hits']['total']['value']
    hits = response['hits']['hits']

    # for hit in hits: 
    #     hit['_source']['id'] = int(hit['_source']['id'])
    return hits_total, hits

def check_all_music(song: Song):
    '''
        add a music to Server Track Database.
    '''
    index_name = 'music' # 使用 match_all 查询获取所有文档 
    query = { "query": { "match_all": {} } } 
    response = es.search(index=index_name, body=query, size=1000)
    hits = response['hits']['hits'] 
    for hit in hits: 
        print(hit['_source'])
    return 


def add_collection(username: str, music_id: str):
    '''
        add a music to User Collection Database.
    '''

    doc_id = str(uuid.uuid4())
    doc = dict(
        id=doc_id,
        username=username,
        music_id=music_id,
    )

    es.index(index='collection', id=doc_id, body=doc)


def delete_collection(doc_id: str):
    '''
        delete a music from User Collection Database.
    '''

    es.delete(index='collection', id=doc_id)


if __name__ == "__main__":
    es = Elasticsearch("http://localhost:9200")
    search_music(keyword='shape', criteria='name', from_=5, size=10)