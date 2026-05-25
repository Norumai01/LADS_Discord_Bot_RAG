import chromadb

# Create a chroma_db folder
client = chromadb.PersistentClient(path="../../chroma_db")

# Create collection (like a table)
collection = client.get_or_create_collection(name="test_collection")

# Store something
collection.add(
    documents=["Hello world!"],
    ids=["Test_1"],
)

# Query it
results = collection.query(query_texts=["Hello world!"], n_results=1)

print(results)

