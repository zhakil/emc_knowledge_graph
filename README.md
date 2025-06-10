# Project Overview

This project contains a collection of Python scripts and modules. The specific functionalities are detailed in the file descriptions below and in individual documentation files.

This README provides general information about the project structure and setup instructions.

## Project Structure

A detailed breakdown of each Python file and its purpose can be found in [FILE_DESCRIPTIONS.md](./FILE_DESCRIPTIONS.md).

The project is organized into several key directories, including:
- `gateway/`: Handles API gateway functionalities, request routing, and middleware.
- `services/`: Contains various microservices or business logic modules, potentially covering AI integration, domain-specific tasks (e.g., EMC), file processing, and knowledge graph operations.
- `kg_construction/`: Scripts related to knowledge graph construction and entity linking.
- `data_processing/`: Utilities for data cleaning and preparation.
- `scripts/`: Utility and automation scripts.
- `tests/`: Unit and integration tests for the project.
- `frontend/`: Contains frontend application code.

For a comprehensive list of all Python files and their specific roles, please refer to the [FILE_DESCRIPTIONS.md](./FILE_DESCRIPTIONS.md).

## Setup and Installation

To set up the development environment for this project, follow these steps:

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a Python virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv .venv
    ```
    (Replace `.venv` with your preferred virtual environment name if desired)

3.  **Activate the virtual environment:**
    -   On Windows:
        ```bash
        .\.venv\Scripts\activate
        ```
    -   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```

4.  **Install dependencies:**
    The project uses two files for dependencies:
    -   `requirements.txt`: For core application dependencies.
    -   `requirements-dev.txt`: For development and testing dependencies.

    Install all dependencies using:
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

5.  **Ready to Go!**
    Your environment should now be set up. You can run the main application scripts or tests as needed.
