import boto3
import json
import chromadb

# Connect to Bedrock for embeddings
bedrock = boto3.client("bedrock-runtime", region_name="eu-north-1")

# Function to convert text to vector using Titan
def get_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

# Read your knowledge file
with open("knowledge.txt", "r") as f:
    lines = [line.strip() for line in f.readlines() if line.strip()]

print(f"Found {len(lines)} lines to index...")

# Create ChromaDB collection
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="aws_knowledge")

# Index each line
for i, line in enumerate(lines):
    embedding = get_embedding(line)
    collection.add(
        documents=[line],
        embeddings=[embedding],
        ids=[f"doc_{i}"]
    )
    print(f"Indexed {i+1}/{len(lines)}: {line[:50]}...")

print("\nAll documents indexed successfully!")
print(f"Total vectors in DB: {collection.count()}")
