from elasticsearch import Elasticsearch


def init_server_track(es):

    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0 # TODO : 0 for devleopment
        },
        "mappings": {
            "properties": {
                "id": {
                    "type": "keyword",
                    "index": True
                },
                "name": {
                    "type": "text",
                    "index": True
                },
                "author": {
                    "type": "text",
                    "index": True
                },
                "duration": {
                    "type": "integer",
                    "index": False
                },
                "lyrics": {
                    "type": "text",
                    "index": True
                },
                "url": {
                    "type": "text",
                    "index": False
                }
            }
        }
    }

    index_name = "music"
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Index '{index_name}' deleted successfully.")

    es.indices.create(index=index_name, body=settings)
    print(f"Index '{index_name}' created successfully.")


def init_user_collection(es):

    settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0 # TODO : 0 for devleopment
        },
        "mappings": {
            "properties": {
                "id": {
                    "type": "keyword",
                    "index": True
                },
                "username": {
                    "type": "text",
                    "index": True
                },
                "music_id": {
                    "type": "keyword",
                    "index": True
                },
            }
        }
    }

    index_name = "collection"
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"Index '{index_name}' deleted successfully.")

    es.indices.create(index=index_name, body=settings)
    print(f"Index '{index_name}' created successfully.")


def init(es):

    if es.ping():
        print("Connected to Elasticsearch")
    else:
        print("Connection failed")

    init_server_track(es)
    init_user_collection(es)


def add_examples(es):
    music_examples = [
        {
            "id": "1",
            "name": "Shape of You",
            "author": "Ed Sheeran",
            "duration": 233,
            "lyrics": "The club isn't the best place to find a lover...",
            "url": "https://example.com/shape_of_you"
        },
        {
            "id": "2",
            "name": "Blinding Lights",
            "author": "The Weeknd",
            "duration": 200,
            "lyrics": "I've been tryna call, I've been on my own for long enough...",
            "url": "https://example.com/blinding_lights"
        },
        {
            "id": "3",
            "name": "Someone Like You",
            "author": "Adele",
            "duration": 285,
            "lyrics": "I heard that you're settled down, That you found a girl and you're married now...",
            "url": "https://example.com/someone_like_you"
        }
    ]

    for music in music_examples:
        res = es.index(index="music", id=music["id"], document=music)
        print(f"Added music with ID: {music['id']}, Result: {res['result']}")


if __name__ == "__main__":
    es = Elasticsearch("http://localhost:9200")
    init(es)
    add_examples(es)