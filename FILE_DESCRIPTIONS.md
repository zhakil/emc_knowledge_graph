# File Descriptions for EMC Knowledge Graph System

This document provides an overview of the main directories and key files within the EMC Knowledge Graph System project.

## Root Directory

-   **`.github/workflows/`**: Contains GitHub Actions CI/CD workflow configurations (e.g., `ci.yml`).
-   **`.venv311/`**: Python virtual environment directory (specific to this setup).
-   **`data_access/`**: Likely intended for data access layer components (currently has `.gitkeep`).
-   **`desktop/`**: Contains files related to the Electron desktop application.
    -   `main.js`: The main process script for Electron. Handles window creation and backend process management.
    -   `package.json`: Defines dependencies and scripts for the Electron app.
    -   `resources/backend/`: Target directory for the packaged Python backend executable.
-   **`docker/`**: Contains Docker-related files, like `compose.yml` for service orchestration.
-   **`frontend/`**: Contains the React frontend application.
    -   `public/`: Static assets for the frontend.
    -   `src/`: Older source structure (might be partially migrated or deprecated).
    -   `components/`: React components organized by function (Display, Editor, EMC, Input).
        -   `Display/GraphVisualization.tsx`: Core ReactFlow component for rendering the knowledge graph.
        -   `Display/KnowledgeGraphViewer.tsx`: Wrapper component that uses `GraphVisualization` and `graphStore` to display the KG.
        -   `Display/OLD_KnowledgeGraphViewer.py`: (Misnamed backend Python code, kept for reference, should be reviewed/moved).
        -   `Editor/DeepSeekPromptEditor.tsx`: UI for editing and sending prompts to DeepSeek.
        -   `Input/FileUploadZone.tsx`: Component for handling file drag-and-drop and selection.
    -   `services/`: Frontend services for API calls (e.g., `aiService.ts`, `fileService.ts`, `graphService.ts`).
    -   `stores/`: Zustand stores for frontend state management (e.g., `deepSeekStore.ts`, `graphStore.ts`, `fileStore.ts`).
    -   `App.tsx`: Main application component, handles routing for different views (Dashboard, AI Chat, KG, File Upload, Settings).
    -   `package.json`: Defines dependencies and scripts for the frontend React app.
-   **`gateway/`**: Contains the FastAPI backend application (API gateway).
    -   `main.py`: Main FastAPI application file, defines API endpoints, middleware, and startup events.
    -   `config.py`: Likely for gateway configuration.
    -   `routing/`: Defines specific API routes (e.g., `deepseek_routes.py`, `file_routes.py`, `graph_routes.py`).
    -   `websocket/`: Websocket communication logic (e.g., `graph_sync.py`).
-   **`nginx/`**: Configuration for Nginx reverse proxy, if used.
-   **`scripts/`**: Various helper and build scripts.
    -   `build_windows_app.py`: Python script to build the Windows executable using PyInstaller and Electron Builder.
    -   `init_databases.sh`: Shell script to initialize databases.
    -   Other utility scripts for deployment, checks, etc.
-   **`services/`**: Backend services (business logic).
    -   `ai_integration/`: Services for integrating with AI models like DeepSeek.
        -   `deepseek_service.py`: Core service for interacting with the DeepSeek API.
        -   `prompt_manager.py`: Manages prompt templates for AI interaction.
    -   `emc_domain/`: Services related to the EMC domain logic (compliance, equipment, standards).
    -   `file_processing/`: Services for handling and processing uploaded files.
    -   `graph_editing/`: Services for real-time graph editing.
    -   `knowledge_graph/`: Services for interacting with the Neo4j knowledge graph.
        -   `neo4j_emc_service.py`: (Referenced in `gateway/main.py` for startup) Python service for Neo4j interactions. Note: `frontend/components/Display/OLD_KnowledgeGraphViewer.py` seems to be a duplicated or misplaced version of this.
-   **`src/types/`**: TypeScript type definitions, primarily for the frontend.
-   **`tests/`**: Automated tests (unit, integration, API).
-   **`utils/`**: Utility functions shared across the backend.
-   **`Dockerfile`**: Dockerfile for building the main application container.
-   **`docker-compose.yml`**: Docker Compose file for orchestrating the application and its services (Neo4j, Postgres, Redis).
-   **`requirements.txt`**: Python dependencies for the backend.
-   **`README.md`**: Main project README file.
-   **`EMC_ONTOLOGY.md`**: Document describing the EMC ontology used in the knowledge graph.

## Key Files Summary

-   **`frontend/App.tsx`**: Central hub of the React frontend application.
-   **`gateway/main.py`**: Entry point and router for all backend API calls.
-   **`services/ai_integration/deepseek_service.py`**: Handles all communication with the DeepSeek AI.
-   **`services/knowledge_graph/neo4j_emc_service.py` (Expected) / `frontend/components/Display/OLD_KnowledgeGraphViewer.py` (Actual, Misplaced)**: Manages interactions with the Neo4j graph database.
-   **`frontend/stores/`**: Contains all Zustand state management stores for the frontend.
-   **`scripts/build_windows_app.py`**: Orchestrates the entire build process for the Windows desktop application.
-   **`docker-compose.yml`**: Defines how all the services (frontend, gateway, databases) run together in a containerized environment.

This list is not exhaustive but covers the most critical parts of the application.
