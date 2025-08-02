# AI Teaching Assistant (Under Development)

This is a work-in-progress project to build an **autonomous multimodal teaching assistant** for multi-grade classrooms. The goal is to empower teachers by automating content generation (text, image, voice) and offering smart planning tools using AI.

## 🔧 What’s Set Up So Far

This monorepo is structured with Docker and includes:

### 🧠 Microservices (FastAPI-based)
- `image-agent`: Receives textbook images and will generate multi-grade worksheets.
- `studyplan-agent`: Processes syllabus PDFs to generate study plans.
- `voice-agent`: Accepts voice queries and will return visual + audio explanations.
- `gateway`: Central API service to route requests from frontend to backend agents.

### 🌐 Frontend (ReactJS)
- PWA-ready React app scaffolded with `create-react-app` to serve as the main UI for teachers.

### 🐳 Dockerized Setup
A single `docker-compose.yml` file runs the entire stack, including:
- Backend microservices
- Frontend UI