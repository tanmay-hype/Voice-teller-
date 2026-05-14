# Voice Teller — Production Architecture & Deployment Flow

# Overview

Voice Teller is an AI-powered storytelling platform that:
- Generates stories using Gemini AI
- Converts stories into speech using Piper TTS or ElevenLabs
- Stores generated audio on Supabase Storage
- Serves frontend globally through Netlify
- Runs backend services inside Docker containers on an Azure Virtual Machine

The system is optimized for a small-scale production workload of approximately 1–10 active users.

---

# High-Level Architecture

```text
User Browser
      │
      ▼
Netlify Frontend (React/Vite)
      │
 HTTPS API Calls
      ▼
Nginx Reverse Proxy (Azure VM)
      │
      ▼
FastAPI Backend (Docker)
      │
 ┌────┴──────────────┐
 │                   │
 ▼                   ▼
Redis           PostgreSQL
 │
 ▼
Celery Worker
 │
 ▼
Piper TTS Service
 │
 ▼
Supabase Storage/CDN
 │
 ▼
Public Audio URL
```

---

# Services Used & Their Purpose

## 1. Microsoft Azure

Service Used:
- Azure Virtual Machine (Ubuntu 24.04)

Purpose:
- Hosts all backend infrastructure
- Runs Docker containers
- Acts as the main application server

Why Azure?
- Free startup credits available
- Full control over infrastructure
- Suitable for Dockerized workloads
- Good balance of flexibility and scalability

What Runs on Azure?
- FastAPI backend
- Redis
- PostgreSQL
- Celery worker
- Piper TTS
- Nginx
- Docker Engine

VM Configuration:

| Component | Value |
|---|---|
| OS | Ubuntu 24.04 LTS |
| VM Type | Standard B2as v2 |
| CPU | 2 vCPUs |
| RAM | 8 GB |
| Architecture | x64 |

---

# 2. Docker

Purpose:
- Containerizes every backend service
- Provides isolated environments
- Simplifies deployment and scaling

Why Docker?
- Consistent environments
- Easy rebuilds
- Easy dependency management
- Simplifies multi-service orchestration

Services Running in Docker:

| Container | Purpose |
|---|---|
| story_api | FastAPI backend |
| story_worker | Celery worker |
| story_db | PostgreSQL database |
| story_redis | Redis broker/cache |
| piper | Piper TTS service |

Docker Compose manages:
- Networking
- Volumes
- Environment variables
- Service dependencies

---

# 3. FastAPI

Purpose:
- Main backend API framework
- Handles:
  - authentication
  - story generation
  - TTS requests
  - database operations
  - API responses

Why FastAPI?
- High performance
- Async support
- Automatic validation
- Swagger/OpenAPI support
- Modern Python ecosystem

Key Responsibilities:

| Feature | Description |
|---|---|
| Authentication | Login/Register |
| Story APIs | Generate stories |
| AI Integration | Gemini API calls |
| Audio APIs | Trigger TTS generation |
| DB Layer | Store users/stories |

---

# 4. Gemini AI

Provider:
- Google Gemini

SDK Used:
- google-genai

Purpose:
- AI story generation
- Dynamic prompt processing
- Creative narrative generation

Model Used:

```text
Gemini 2.5 Flash
```

Fallback Models:
- gemini-2.0
- gemini-1.5-flash

Why Gemini?
- Fast inference
- Lower cost
- Good storytelling quality
- Simple API integration

Generation Flow:

```text
User Prompt
     ↓
FastAPI
     ↓
Gemini API
     ↓
Generated Story
```

---

# 5. Celery

Purpose:
- Background task processing

Why Celery?
- Prevents long-running tasks from blocking API responses
- Handles asynchronous processing

Tasks Handled:
- TTS generation
- Audio uploads
- Background processing

Flow:

```text
API Request
    ↓
Celery Queue
    ↓
Worker Executes Task
```

---

# 6. Redis

Purpose:
- Message broker for Celery
- Temporary caching layer

Why Redis?
- Extremely fast
- Lightweight
- Industry standard for Celery

Redis Responsibilities:

| Use | Description |
|---|---|
| Broker | Queue communication |
| Backend | Task result storage |
| Cache | Temporary in-memory storage |

---

# 7. Piper TTS

Purpose:
- Local text-to-speech generation

Why Piper?
- Fully offline
- No API costs
- Lightweight
- Good voice quality

How It Works:

```text
Story Text
     ↓
Piper HTTP Service
     ↓
Audio WAV Generated
```

Deployment Style:
- Dedicated Docker container
- Internal Docker networking
- Accessed through:

```text
http://piper:8080
```

Voice Model Used:

```text
en_US-amy-medium.onnx
```

---

# 8. ElevenLabs

Purpose:
- Premium AI voice generation
- Voice cloning

Used For:
- Enhanced voice quality
- Optional premium TTS

Why Keep Both Piper and ElevenLabs?

| Piper | ElevenLabs |
|---|---|
| Free | Paid API |
| Offline | Cloud-based |
| Fast | Higher quality |
| Self-hosted | External service |

---

# 9. PostgreSQL

Purpose:
- Primary relational database

Stores:

| Data | Example |
|---|---|
| Users | accounts |
| Stories | generated stories |
| Audio URLs | Supabase links |
| Metadata | timestamps |

Why PostgreSQL?
- Reliable
- Strong relational support
- Production-grade
- Excellent Python support

Running As:
- Docker container
- Internal network only

---

# 10. Supabase Storage

Purpose:
- Audio file storage
- CDN delivery

Why Supabase?
- Free storage tier
- Public file URLs
- Easy integration
- CDN-backed delivery

Flow:

```text
Piper Audio
     ↓
Supabase Upload
     ↓
Public CDN URL
     ↓
Frontend Playback
```

Stored Content:
- WAV files
- MP3 files
- Generated speech audio

Bucket Used:

```text
story-audio
```

---

# 11. Netlify

Purpose:
- Frontend hosting

Frontend Stack:
- React
- Vite

Why Netlify?
- Free hosting
- CI/CD from GitHub
- Global CDN
- Automatic HTTPS

Deployment Flow:

```text
GitHub Push
     ↓
Netlify Build
     ↓
Global Frontend Deployment
```

Frontend Responsibilities:
- User interface
- API communication
- Audio playback
- Authentication forms
- Story generation UI

---

# 12. Nginx

Purpose:
- Reverse proxy
- HTTPS termination
- Traffic forwarding

Why Nginx?
- Production-grade web server
- Efficient reverse proxy
- SSL support
- Security layer

Flow:

```text
Internet Traffic
      ↓
Nginx
      ↓
FastAPI Container
```

Responsibilities:

| Task | Description |
|---|---|
| HTTPS | SSL termination |
| Proxy | Forward requests |
| Security | Public access layer |
| Routing | Domain handling |

---

# 13. DuckDNS

Purpose:
- Free domain provider

Domain Used:

```text
voice-teller-ai.duckdns.org
```

Why DuckDNS?
- Free subdomain
- Easy setup
- Good for small deployments

---

# 14. Certbot + Let's Encrypt

Purpose:
- Automatic HTTPS certificates

Why?
- Enables secure HTTPS
- Prevents mixed-content browser errors
- Encrypts traffic

Certificate Flow:

```text
Certbot
    ↓
Let's Encrypt
    ↓
SSL Certificate
    ↓
Nginx HTTPS
```

---

# Request Lifecycle Example

## Story Generation Flow

```text
1. User enters prompt
2. Frontend sends API request
3. FastAPI receives request
4. Gemini generates story
5. Story stored in PostgreSQL
6. Response returned to frontend
```

---

# Audio Generation Flow

```text
1. User clicks Read Story
2. FastAPI triggers TTS
3. Piper generates audio
4. Audio converted into bytes
5. Uploaded to Supabase
6. Public URL generated
7. URL stored in PostgreSQL
8. Frontend plays audio
```

---

# Security Architecture

## HTTPS

All public traffic uses HTTPS through:
- Nginx
- Let's Encrypt certificates

---

## Internal Networking

Docker services communicate internally:

```text
api → redis
api → postgres
api → piper
worker → redis
worker → postgres
```

These services are NOT exposed publicly.

---

# Scalability Notes

Current Target:
- 1–10 users

Current Architecture Is Suitable For:
- MVP
- Portfolio project
- Early-stage SaaS
- Small production workloads

Future Scaling Improvements:

| Upgrade | Benefit |
|---|---|
| Azure Container Apps | Auto scaling |
| Managed PostgreSQL | Better DB reliability |
| Kubernetes | Large-scale orchestration |
| GPU TTS | Faster generation |
| CDN caching | Better audio performance |

---

# Final Tech Stack Summary

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Frontend Hosting | Netlify |
| Backend API | FastAPI |
| AI | Gemini |
| Queue System | Celery |
| Broker | Redis |
| Database | PostgreSQL |
| TTS | Piper + ElevenLabs |
| File Storage | Supabase |
| Reverse Proxy | Nginx |
| HTTPS | Certbot + Let's Encrypt |
| Infrastructure | Azure VM |
| Containerization | Docker |

---

# Conclusion

Voice Teller is built using a modern cloud-native architecture that combines:
- AI generation
- asynchronous processing
- containerized deployment
- CDN-based media delivery
- HTTPS-secured infrastructure

The deployment is optimized for:
- low operational cost
- easy maintenance
- small-scale production traffic
- future scalability

This architecture provides a strong foundation for expanding the platform into a larger AI storytelling SaaS application.

