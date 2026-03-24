import boto3
import json
import math
from datetime import datetime

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="eu-north-1")
dynamodb = boto3.resource("dynamodb", region_name="eu-north-1")
cloudwatch = boto3.client("cloudwatch", region_name="eu-north-1")
table = dynamodb.Table("rag-chat-history")
BUCKET = "rag-chatbot-lakshmireddy"

def put_metric(name, value, unit="Count"):
    cloudwatch.put_metric_data(
        Namespace="RAGChatbot",
        MetricData=[{
            "MetricName": name,
            "Value": value,
            "Unit": unit
        }]
    )

def get_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text[:8000]})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

def cosine_similarity(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    mag_a = math.sqrt(sum(x*x for x in a))
    mag_b = math.sqrt(sum(x*x for x in b))
    return dot / (mag_a * mag_b)

def load_embeddings_from_s3():
    docs = []
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix="embeddings/")
    for obj in response.get("Contents", []):
        data = s3.get_object(Bucket=BUCKET, Key=obj["Key"])
        chunks = json.loads(data["Body"].read().decode("utf-8"))
        docs.extend(chunks)
    return docs

def search_context(question, docs):
    q_embedding = get_embedding(question)
    scores = []
    for doc in docs:
        score = cosine_similarity(q_embedding, doc["embedding"])
        scores.append((score, doc["text"]))
    scores.sort(reverse=True)
    return "\n".join([text for _, text in scores[:3]])

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
    start_time = datetime.utcnow()
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
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "No question provided"})
            }

        docs = load_embeddings_from_s3()
        context_text = search_context(question, docs)
        history = get_chat_history(session_id)
        answer = ask_claude(question, context_text, history)
        save_to_history(session_id, question, answer)

        duration = (datetime.utcnow() - start_time).total_seconds() * 1000
        put_metric("QuestionsAnswered", 1)
        put_metric("ResponseTime", duration, "Milliseconds")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "answer": answer,
                "session_id": session_id
            })
        }

    except Exception as e:
        put_metric("Errors", 1)
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
