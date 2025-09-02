# AI Teaching Assistant

An **autonomous multimodal teaching assistant** for multi-grade classrooms.  
The goal is to empower teachers by automating content generation (text, image, voice) and offering smart planning tools using AI.

---

## � Current Features

This monorepo is structured with Docker and includes the following microservices:

### � Microservices (FastAPI-based)

- **`studyplan-agent`**  
  - Input: syllabus PDF (`file_id`)  
  - Output: structured weekly study plan (overview, outcomes, checks, resources)  

- **`image-agent`**  
  - Input: textbook page image (`file_id`)  
  - Output: worksheet questions (MCQ, short, diagram) + printable PDF  

- **`voice-agent`** *(planned)*  
  - Input: teacher/student voice query (`file_id`)  
  - Output: transcript + explanation (text/visual) + audio reply  

- **`gateway`**  
  - Central API service that routes frontend requests to backend agents  
  - Contracts defined via Pydantic models (single source of truth)

---

## � Frontend

- ReactJS Progressive Web App scaffolded with `create-react-app`  
- Will serve as the main UI for teachers:  
  - Upload syllabus PDFs / textbook images  
  - View generated study plans and worksheets  
  - (Planned) Ask voice questions and receive audio answers  

---

## � Dockerized Setup

A single `docker-compose.yml` file runs the entire stack:

- Backend microservices (`studyplan-agent`, `image-agent`, `voice-agent` (planned), `gateway`)  
- Frontend UI (React)  

### Run locally

```bash
# build and start all services
docker compose up -d --build

# check running containers
docker compose ps

# view logs (e.g., studyplan-agent)
docker compose logs -f studyplan
```