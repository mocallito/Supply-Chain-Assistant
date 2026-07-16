from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")

client.delete_collection(
    collection_name="restaurant_reviews"
)

for collection in client.get_collections().collections:
    name = collection.name
    info = client.get_collection(name)

    print(
        f"{name}: "
        f"{info.points_count} points"
    )
