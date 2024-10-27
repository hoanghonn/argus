# Argus - Elsa's coding challenge

Argus is the Greek God of All-seeing. 


[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Getting Started

The project will run completely with Docker and Docker Compose for easy-to-install and easy-to-run setup.

### Required Installations
- Docker: If you don’t have it yet, follow the [installation instructions](https://docs.docker.com/get-started/get-docker/#supported-platforms).
- Docker Compose: Refer to the official documentation for the [installation guide](https://docs.docker.com/compose/install/).

### Commands
After installing all required technologies, simply run this command:

```bash
docker compose -f docker-compose.local.yml up --build
```

Then you can access Argus with http://localhost:8000. Enjoy quizzing!
## Challenge Requirements

### Part 1: System Design

- [x] **[Architecture Diagram, Component Descriptions, Data Flow, Technologies and Tools](specs/SystemSpec.md)**: A comprehensive System Design Document that includes an architecture diagram, component descriptions, data flow explanations, and a justification for the technologies and tools chosen for each component.
  
### Part 2: Implementation

- [x] **Real-time Quiz Participation**: Enabled users to join a quiz session using a unique quiz ID.
- [x] **Real-time Score Updates**: Users’ scores update in real-time as they submit answers.
- [x] **Real-time Leaderboard**: Displayed a real-time leaderboard showing the current standings of all participants.
