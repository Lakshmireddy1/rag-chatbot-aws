AWS RAG Chatbot (Production-Grade Serverless AI System)

A scalable, serverless Retrieval-Augmented Generation (RAG) chatbot built entirely on AWS, designed for real-world enterprise use cases such as internal knowledge assistants, customer support automation, and document intelligence.


Architecture Overview

This system follows a fully serverless, event-driven architecture optimized for scalability, cost-efficiency, and low operational overhead.

Core Stack

AWS Bedrock — Claude Sonnet (LLM), Titan Embeddings
AWS Lambda — Stateless compute for inference + ingestion
AWS API Gateway — Secure REST API interface
AWS S3 — Document storage + vector index persistence
AWS DynamoDB — Session memory + conversation history
AWS CloudWatch — Logs, metrics, monitoring dashboards


System Design

🔹Request Flow (Inference Pipeline)

Client → API Gateway → Lambda → Vector Retrieval → Bedrock → Response → DynamoDB

🔹 Ingestion Pipeline (Event-Driven)

S3 Upload → Lambda Trigger → Chunking → Embeddings → Vector Store Update


Features

- Dynamic Document Ingestion — Upload ".txt" files to S3 and auto-index instantly
-RAG-based Contextual Responses — Accurate answers using vector similarity search
- Multi-turn Conversations — Session-aware chat using DynamoDB
- Fully Serverless Architecture — No infrastructure management required
- Production Monitoring — CloudWatch logs, metrics, and alerts
- Scalable & Cost-Optimized — Pay-per-use model

Security & Governance

- IAM roles with least privilege access
- API Gateway throttling and request validation
- Secure service-to-service communication (Lambda ↔ Bedrock, S3, DynamoDB)
- No hardcoded credentials (uses IAM roles)

Performance Metrics

- Average Response Time: ~1–2 seconds
- Cold Start Latency: ~2–3 seconds
- Vector Retrieval Time: < 200ms
- System Scalability: Auto-scales with Lambda concurrency


Cost Analysis (Free Tier Optimized)

Service| Estimated Cost
Lambda| ~$1–2/month (low usage)
Bedrock| Pay-per-token (~$0.01/test)
S3| Negligible
DynamoDB| Free tier eligible

Optimization Strategies

- Reduced token usage via efficient chunking
- Serverless architecture eliminates idle cost
- Event-driven ingestion minimizes compute usage


Design Decisions

- Serverless-first approach → Eliminates infrastructure overhead
- Bedrock over self-hosted models → Faster deployment, managed scaling
- DynamoDB for session memory → Low latency + high scalability
- S3 for vector storage → Durable and cost-efficient
- Lambda orchestration → Simplifies integration and scaling


API Usage

Endpoint

POST /chat

Request

{
  "question": "What is AWS Lambda?",
  "session_id": "session_id"
}

Response

{
  "answer": "AWS Lambda is a serverless compute service..."
}


Setup Instructions

1. Create S3 bucket for document storage
2. Deploy Lambda functions (chat + ingestion)
3. Configure API Gateway routes
4. Create DynamoDB table for session storage
5. Enable Bedrock model access (Claude + Titan)
6. Configure IAM roles with required permissions


Live API

https://ku3h398jk9.execute-api.eu-north-1.amazonaws.com/prod/chat


Future Enhancements

- Add semantic caching for faster responses
- Implement multi-document support (PDF, DOCX)
- Integrate frontend UI (React / Streamlit)
- Add authentication layer (JWT / Cognito)
- Improve observability with tracing (X-Ray)


Conclusion

This project demonstrates the ability to:

- Design and deploy production-grade AI systems
- Build scalable serverless architectures on AWS
- Implement real-world RAG pipelines with LLMs
- Optimize for cost, performance, and maintainability

Author

Built by an AWS Engineer transitioning into AI Systems Engineering, focused on delivering scalable, intelligent cloud solutions.
