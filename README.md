# AWS RAG Chatbot

A production-grade Retrieval Augmented Generation (RAG) chatbot built entirely on AWS.

## Architecture
- **AWS Bedrock** — Claude Sonnet 4 for LLM, Titan Embeddings for vectors
- **AWS Lambda** — Serverless compute for chatbot and document ingestion
- **AWS S3** — Document storage and vector embeddings store
- **AWS API Gateway** — Public REST API endpoint
- **AWS DynamoDB** — Conversation history and session memory
- **AWS CloudWatch** — Monitoring, dashboards and alerts

## Features
- Dynamic document ingestion — upload any .txt file to S3, auto-indexed instantly
- Multi-turn conversations with session memory via DynamoDB
- Vector similarity search for relevant context retrieval
- Production monitoring with custom CloudWatch metrics
- Fully serverless — zero infrastructure management

## API Usage
POST /chat
```json
{
  "question": "What is AWS Lambda?",
  "session_id": "user-123"
}
```

## Setup
1. Create S3 bucket
2. Deploy Lambda functions
3. Configure API Gateway
4. Set up DynamoDB table
5. Enable Bedrock model access

## Live API
```
https://ku3h398jk9.execute-api.eu-north-1.amazonaws.com/prod/chat
```
