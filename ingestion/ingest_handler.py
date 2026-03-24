import boto3
import json

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="eu-north-1")

def get_embedding(text):
    response = bedrock.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text[:8000]})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    for word in words:
        current_chunk.append(word)
        current_size += len(word)
        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

def lambda_handler(event, context):
    try:
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]

        print(f"Processing: {key} from {bucket}")

        obj = s3.get_object(Bucket=bucket, Key=key)
        text = obj["Body"].read().decode("utf-8")

        chunks = chunk_text(text)
        print(f"Created {len(chunks)} chunks")

        embeddings_store = []
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            embeddings_store.append({
                "id": f"{key}_chunk_{i}",
                "text": chunk,
                "embedding": embedding
            })
            print(f"Indexed chunk {i+1}/{len(chunks)}")

        output_key = key.replace(".txt", "_embeddings.json")
        s3.put_object(
            Bucket=bucket,
            Key=f"embeddings/{output_key}",
            Body=json.dumps(embeddings_store)
        )

        print(f"Saved {len(embeddings_store)} embeddings to S3")
        return {"statusCode": 200, "body": f"Indexed {len(chunks)} chunks"}

    except Exception as e:
        print(f"Error: {str(e)}")
        raise e
