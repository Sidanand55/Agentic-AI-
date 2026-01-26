# Agentic-AI

Experiments combining LangGraph workflows, vector-backed memory, and voice-first agents.

## Project structure
- [langgraph_learn/chat.py](langgraph_learn/chat.py): Minimal LangGraph chat flow (START → chatbot → samplenode → END).
- [langgraph_learn/chat_conditional_edge.py](langgraph_learn/chat_conditional_edge.py): Conditional routing with OpenAI (fallbacks and branching).
- [langgraph_learn/chat_mongo.py](langgraph_learn/chat_mongo.py): LangGraph with MongoDB checkpointing for thread persistence.
- [mem_agent/mem.py](mem_agent/mem.py): Mem0 + Qdrant vector store + OpenAI to recall/add user memories in a loop.
- [voice_agent/main.py](voice_agent/main.py): Simple voice agent (speech-to-text → chat completion → TTS playback).
- [voice_agent/cursor.py](voice_agent/cursor.py): Chain-of-thought voice agent with tool use (weather, shell commands) and TTS.

## Prerequisites
- Python 3.10+
- Docker (for MongoDB + Qdrant)
- Environment: `OPENAI_API_KEY` (and optional `MONGO` creds if changed)

## Setup
1) Install deps:
```sh
pip install -r requirements.txt
```
2) Start services:
```sh
docker-compose up -d
```
   - MongoDB: `mongodb://admin:admin@localhost:27017`
   - Qdrant: `http://localhost:6333`

## How to run
- LangGraph basics: `python langgraph_learn/chat.py`
- LangGraph with conditional edge: `python langgraph_learn/chat_conditional_edge.py`
- LangGraph with Mongo checkpointing: `python langgraph_learn/chat_mongo.py`
- Memory agent loop: `python mem_agent/mem.py`
- Voice agent (simple): `python voice_agent/main.py`
- Voice agent with tools + CoT: `python voice_agent/cursor.py`

Ensure microphone access for voice agents; they use Google STT and OpenAI TTS.

## Notes
- Checkpointing uses MongoDB via LangGraph’s MongoDBSaver.
- Memory agent stores/retrieves embeddings in Qdrant via Mem0.
- Voice flows stream TTS using `gpt-4o-mini-tts` and play audio locally.
