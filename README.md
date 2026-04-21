# Autonomous AI Execution Engine 🤖📈

A lightweight, cloud-deployed algorithmic trading daemon that ingests live market data, utilizes Large Language Models (LLMs) for micro-trend analysis, and securely executes REST API orders via cryptographic signatures.

## ⚙️ System Architecture

This project demonstrates a complete production-grade data pipeline and AI orchestration logic, bypassing standard pre-built libraries to showcase core backend engineering principles.

*   **Data Ingestion:** Pings global exchange REST APIs to pull real-time asset pricing.
*   **Persistent Memory:** Maps and maintains a local database (CSV) to provide historical context to the LLM.
*   **AI Orchestration:** Integrates with the **Groq API (Llama 3.1)**. Utilizes advanced prompt engineering to force the generative AI to output strict, machine-readable `JSON` instead of conversational text.
*   **Risk Management Logic:** Programmatic logic gates that intercept AI decisions, blocking execution if the AI's mathematically derived "confidence score" drops below operational thresholds.
*   **Cryptographic Execution:** Bypasses beginner-level wrappers by manually constructing and signing `HMAC-SHA256` cryptographic payloads to securely authenticate and fire live market orders.
*   **Webhook Alerting:** Pushes live, formatted execution alerts and AI reasoning to a dedicated Discord server via webhooks.
*   **Cloud Infrastructure:** Designed to run headless as an untethered Linux daemon (`nohup`) on remote virtual private servers.

## 🛠️ Tech Stack
*   **Language:** Python 3
*   **AI Integration:** Groq API (Llama 3.1 8b/70b)
*   **Security:** `hashlib`, `hmac`, `dotenv`
*   **Networking:** `requests`, `urllib`

*Note: This repository represents the architectural framework of an autonomous agent. API keys and environmental variables have been secured and removed from the public repository.*
