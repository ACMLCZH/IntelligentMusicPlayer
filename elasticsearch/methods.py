import uuid
from elasticsearch import Elasticsearch


es = Elasticsearch(["http://localhost:9200"])

def add_music(name: str, author: str, duration: int, lyrics: str, url: str):
    '''
        add music to Server Track Database.
    '''

    doc_id = str(uuid.uuid4())
    doc = dict(
        id=doc_id,
        name=name,
        author=author,
        duration=duration,
        lyrics=lyrics,
        url=url
    )

    es.index(index='music', id=doc_id, body=doc)


def delete_music(doc_id: str):
    '''
        delete music from Server Track Database.
    '''

    es.delete(index='music', id=doc_id)


def search_music(keyword: str, criteria: str, from_: int, size: int):
    '''
        search music in Server Track Database.
    '''

    if criteria == 'all':
        query = {
            "query_string": {
                "query": keyword
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
    hits = [hit['_source'] for hit in response['hits']['hits']]

    # import pdb; pdb.set_trace()

    return hits_total, hits


def get_music(music_ids: list[str], source: list[str]):
    '''
        get music based on music_ids
    '''

    query = {
        "terms": {
            "_id": music_ids
        }
    }

    response = es.search(index='music', query=query, source=source)

    hits_total = response['hits']['total']['value']
    hits = [hit['_source'] for hit in response['hits']['hits']]

    # import pdb; pdb.set_trace()

    return hits_total, hits


def add_collection(username: str, collection_name: str, music_id: str):
    '''
        add music to User Collection Database.
    '''

    doc_id = str(uuid.uuid4())
    doc = dict(
        id=doc_id,
        username=username,
        collection_name=collection_name,
        music_id=music_id,
    )

    es.index(index='collection', id=doc_id, body=doc)


def delete_collection(doc_id: str):
    '''
        delete music from User Collection Database.
    '''

    es.delete(index='collection', id=doc_id)


def get_collection(username: str, collection_name: str):
    '''
        get a list of music_id in a collection
    '''

    query = {
        "bool": {
            "must": [
                {"term": {"username": username}},
                {"term": {"collection_name": collection_name}}
            ]
        }
    }

    response = es.search(
        index="collection",
        body={
            "query": query,
            "_source": ["music_id"]
        }
    )

    music_ids = [hit["_source"]["music_id"] for hit in response["hits"]["hits"]]

    return music_ids


if __name__ == "__main__":
    es = Elasticsearch("http://localhost:9200")
    # search_music(keyword='shape', criteria='name', from_=5, size=10)
    print(get_music(get_collection(username='user', collection_name='fav'), source=['id', 'name', 'author', 'duration']))