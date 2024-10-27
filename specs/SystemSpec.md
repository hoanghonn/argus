# System Specifications

Argus is a streamlined, efficient platform for conducting and monitoring quiz sessions, designed for seamless user experience and robust performance.

## Architecture Overview

Argus follows a microservices-based architecture, with each component serving a specific function, simplifying deployment, scaling, and maintenance. The design prioritizes efficiency by only including essential tools; optional components, labeled as such, are available to enhance functionality.

### Architecture Diagram

![Architecture Diagram](architecture-diagram.jpg)

The diagram below represents Argus's architecture, emphasizing simplicity and modularity. Optional components, which provide additional functionalities but are not strictly required, are indicated as such.

## Component Description

### Main Server

The primary server, implemented with **Python and Django**, follows the **Model-View-Template (MVT)** pattern to simplify code organization and enhance maintainability.

- **Responsibilities**:
  - **Database Management**: The server interfaces with PostgreSQL to handle data storage and retrieval. There are two primary tables:
    - **QuizSession**: Tracks each quiz session as a unique object that users can join, view, and monitor.
    - **QuizScore**: Stores scores per user per session, linked to the respective `QuizSession`.
  - **WebSocket Connections**: Leveraging Django Channels, the server supports real-time WebSocket connections for quiz updates and live score tracking.
    - **Channel Layers**: Uses **Redis** as an in-memory database to manage WebSocket routing and connection states.
  - **Template Rendering**: Generates dynamic HTML templates to render user interfaces, including:
    - **Main Room**: Entry point for users to join or create sessions.
    - **Quiz Room**: Displays real-time quiz questions and options.
    - **Monitor**: Shows real-time participant activity for administrators.
    - **Review Page**: Provides detailed post-session statistics and scores.

### Background Workers

Argus employs **Celery** for asynchronous task processing, with Redis as the message broker to facilitate communication between services. These workers run independently of the main server, handling background tasks such as:

- **Timer Management**: Manages countdown timers for quiz questions, ensuring precise time control across user sessions.

![Timer Diagram](timer.jpg)

### Database: PostgreSQL

Argus utilizes PostgreSQL for persistent data storage.

- **QuizSession Table**: Records each quiz session, including metadata like session name, start time, and active participants.
- **QuizScore Table**: Holds individual scores, linked to specific `QuizSession` instances for organized score tracking.

*Refer to the ER Diagram below for table relationships and data structure overview.*

![ER Diagram](er-diagram.png)

### In-Memory Database: Redis

Redis serves two main functions in Argus:

- **Channel Layers**: Used by Django Channels to store WebSocket connection routing data, allowing real-time updates without excessive database load.
- **Message Broker**: Facilitates communication between the main server and Celery workers, enabling quick message relay for task execution, particularly for managing timers and handling background tasks.

## Data Flow

The following steps outline the data flow for a typical user interaction within Argus:

1. **Session Creation**: A new session is initiated by a user in the Main Room, and a `QuizSession` entry is created in PostgreSQL.
2. **Real-Time Updates**: As participants join, Redis Channel Layers update WebSocket connections to ensure real-time data sharing.
3. **Question Timer**: Celery manages quiz question timers via Redis, sending periodic updates back to the WebSocket for live display.
4. **Score Tracking**: Each user's response is recorded and stored in `QuizScore`, which is updated dynamically during the session.
5. **Session Completion**: After the quiz, participants are redirected to the Review Page, where scores and statistics are displayed.

This architecture ensures responsive, real-time interaction with minimal latency, providing an engaging and interactive experience for users.

---

This Markdown format preserves the headings, bold text, and inline links, making it suitable for documentation files or web platforms like GitHub.