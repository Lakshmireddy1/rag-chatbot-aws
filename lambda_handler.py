import boto3
import json
from datetime import datetime

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="eu-north-1")
dynamodb = boto3.resource("dynamodb", region_name="eu-north-1")
table = dynamodb.Table("rag-chat-history")
BUCKET = "rag-chatbot-lakshmireddy"

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "POST,OPTIONS"
}

def load_docs_from_s3():
    docs = []
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix="embeddings/")
    for obj in response.get("Contents", []):
        data = s3.get_object(Bucket=BUCKET, Key=obj["Key"])
        chunks = json.loads(data["Body"].read().decode("utf-8"))
        for chunk in chunks:
            docs.append(chunk["text"])
    return docs

def keyword_search(question, docs, top_k=3):
    question_words = set(question.lower().split())
    scores = []
    for doc in docs:
        doc_words = set(doc.lower().split())
        score = len(question_words & doc_words)
        scores.append((score, doc))
    scores.sort(reverse=True)
    return "\n".join([doc for _, doc in scores[:top_k]])

def get_chat_history(session_id):
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("session_id").eq(session_id)
    )
    messages = []
    for item in response["Items"]:
        messages.append({"role": "user", "content": item["question"]})
        messages.append({"role": "assistant", "content": item["answer"]})
    return messages[-6:] if len(messages) > 6 else messages

def save_to_history(session_id, question, answer):
    table.put_item(Item={
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer
    })

def ask_claude(question, context, history):
    system = f"""You are an AWS expert assistant.
Use only the context below to answer questions.
Context:
{context}"""
    messages = history + [{"role": "user", "content": question}]
    response = bedrock.invoke_model(
        modelId="eu.anthropic.claude-sonnet-4-20250514-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "system": system,
            "messages": messages
        })
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]

def lambda_handler(event, context):
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 200, "headers": CORS_HEADERS, "body": ""}

    try:
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        elif isinstance(event.get("body"), dict):
            body = event["body"]
        else:
            body = event

        question = body.get("question", "")
        session_id = body.get("session_id", "default")

        if not question:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"error": "No question provided"})
            }

        docs = load_docs_from_s3()
        context_text = keyword_search(question, docs)
        history = get_chat_history(session_id)
        answer = ask_claude(question, context_text, history)
        save_to_history(session_id, question, answer)

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"answer": answer, "session_id": session_id})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }
