import boto3
import json
import chromadb

bedrock = boto3.client("bedrock-runtime", region_name="eu-north-1")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="aws_knowledge")

def get_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

def search_context(question):
    embedding = get_embedding(question)
    results = collection.query(
        query_embeddings=[embedding],
        n_results=3
    )
    return "\n".join(results["documents"][0])

def ask_claude(question, context):
    prompt = f"""You are an AWS expert assistant.
Use only the context below to answer the question.

Context:
{context}

Question: {question}

Answer:"""

    response = bedrock.invoke_model(
        modelId="eu.anthropic.claude-sonnet-4-20250514-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

print("AWS RAG Chatbot ready! Type 'quit' to exit.\n")
while True:
    question = input("You: ")
    if question.lower() == "quit":
        break
    context = search_context(question)
    answer = ask_claude(question, context)
    print(f"\nClaude: {answer}\n")
