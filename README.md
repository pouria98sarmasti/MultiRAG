
# MultiRAG

## 1. Introduction

MultiRAG is an advanced Retrieval-Augmented Generation (RAG) applications. It enables the integration of multiple retrieval strategies and large language models (LLMs) to enhance the accuracy and relevance of generated responses. Including Adaptive-RAG, Corrective-RAG, Self-RAG.

MultiRAG implements two level of users (admin, regular user) in which admin can upload its dataset (pdf, docx, csv) and specify user access to each dataset for RAG.

## 2. Tech Stack

MultiRAG is built with the following key technologies:

*   **Python**: The core programming language for the backend logic and LLM integrations.
*   **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
*   **SQLAlchemy**: An SQL toolkit and Object-Relational Mapper (ORM) that provides a full suite of well-known persistence patterns for access to relational databases.
*   **PostgreSQL**: A powerful, open-source object-relational database system.
*   **LangChain**: A framework for developing applications powered by language models.
*   **Vector Databases (PGVector)**: Used for efficient similarity search and retrieval of document embeddings.
*   **Docker & Docker Compose**: For containerization and easy deployment of the application and its services.
*   **Logging**: Structured logging for better observability and debugging.

## 3. Project Structure

The project is organized into the following main directories:

*   `config/`: Configuration files for the application.
*   `data/`: Stores temporary raw data, such as PDF, CSV, DOCX documents.
*   `src/`: Contains the core source code, further divided into:
    *   `llm/`: Modules related to Large Language Models, including base LLMs, RAG-specific LLMs, and prompt definitions.
    *   `models/`: SQLAlchemy models defining the database schema.
    *   `operations/`: Business logic and database operations.
    *   `schema/`: Pydantic schemas for request and response validation.
    *   `utils/`: Utility functions, including logging and configuration management.
*   `web/`: Web application components, including FastAPI routers, API definitions, and custom exceptions.
*   `tests/`: Unit and integration tests.
*   `logs/`: Application logs.
*   `docker-compose.yaml`: Docker Compose file for setting up the development and production environment.
*   `pyproject.toml`: Project configuration for poetry.
*   `README.md`: This file.

## 4. Setup Instructions

### Local Development

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/pouria98sarmasti/MultiRAG.git
    cd MultiRAG
    ```

2.  **Install uv:**
    [installation guid](https://docs.astral.sh/uv/getting-started/installation/)
3.  **Install dependencies:**
    ```bash
    uv add lock
    uv add sync
    ```

4.  **Activate the virtual environment:**
    ```bash
    # windows
    source .venv/Scripts/activate

    # linux
    source .venv/bin/activate
    ```


5.  **Start the application:**
    ```bash
    uvicorn web.app_api:app --reload
    ```

    The application will be accessible at `http://127.0.0.1:2011`.

### Docker Deployment

1.  **Build and run with Docker Compose:**
    ```bash
    docker compose up --build -d
    ```

2.  **Access the application:**
    The application will be accessible at `http://localhost:2011` (or the port specified in your `docker-compose.yaml`).

3.  **Stop the application:**
    ```bash
    docker compose down
    ```

## 5. API Documentation

The MultiRAG API is built with FastAPI and provides the following endpoints:

### User Endpoints (`/user`)

*   **`POST /chat/create`**
    *   **Description**: Creates a new chat session for a user.
    *   **Request Body**:
        ```json
        {
            "name": "My New Chat",
            "llm_type": "some_llm_type",
            "user_id": "a_valid_uuid",
            "rag_system_id": "another_valid_uuid"
        }
        ```
    *   **Response**: Returns the created chat session object.

*   **`GET /chat`**
    *   **Description**: Lists all chat sessions for a given user.
    *   **Query Parameters**:
        *   `user_id` (UUID): The ID of the user.
    *   **Response**: Returns a list of chat session objects.

*   **`POST /chat/history`**
    *   **Description**: Retrieves the chat history for a specific session.
    *   **Request Body**:
        ```json
        {
            "user_id": "a_valid_uuid",
            "session_id": "a_valid_uuid"
        }
        ```
    *   **Response**: Returns a list of chat messages for the session.

*   **`DELETE /chat`**
    *   **Description**: Deletes a specific chat session and its history.
    *   **Request Body**:
        ```json
        {
            "user_id": "a_valid_uuid",
            "session_id": "a_valid_uuid"
        }
        ```
    *   **Response**: Returns a confirmation message.

*   **`POST /chat`**
    *   **Description**: Sends a user prompt to the LLM within a specific chat session and streams the response.
    *   **Request Body**:
        ```json
        {
            "user_prompt": "Hello, how does MultiRAG work?",
            "llm_type": "some_llm_type",
            "user_id": "a_valid_uuid",
            "session_id": "a_valid_uuid",
            "rag_system_id": "another_valid_uuid"
        }
        ```
    *   **Response**: Streams the LLM's response.

### File Endpoints (`/file`)

These endpoints are used for uploading and downloading files, primarily datasets.

*   **`POST /file`**
    *   **Description**: Uploads a file (dataset) to the system, saves it locally, and stores its metadata and content in the database.
    *   **Request Form Data**:
        *   `file` (File): The file to upload.
        *   `data` (JSON/Form): Additional data for the file.
            ```json
            {
                "file_name": "MyDocument",
                "expertise": "AI",
                "admin_id": "a_valid_uuid"
            }
            ```
    *   **Response**: Returns the created dataset information object.

*   **`GET /file`**
    *   **Description**: Downloads a specific dataset by its ID.
    *   **Query Parameters**:
        *   `dataset_id` (UUID): The ID of the dataset to download.
    *   **Response**: Returns the file as a downloadable attachment.

*   **`GET /file/filename`**
    *   **Description**: Retrieves the filename of a dataset given its ID.
    *   **Query Parameters**:
        *   `dataset_id` (UUID): The ID of the dataset.
    *   **Response**: Returns an object containing the filename.

### Admin Endpoints (`/admin`)

The admin endpoints are categorized for user management, dataset management, RAG system management, and RAG system access management.

#### Admin-User Management

*   **`POST /user`**
    *   **Description**: Creates a new user.
    *   **Request Body**:
        ```json
        {
            "username": "new_user",
            "user_id": "a_unique_uuid"
        }
        ```
    *   **Response**: Returns the created user object.

*   **`GET /user`**
    *   **Description**: Lists all registered users.
    *   **Response**: Returns a list of user objects.

*   **`DELETE /user`**
    *   **Description**: Deletes a user and their associated chat history.
    *   **Query Parameters**:
        *   `user_id` (UUID): The ID of the user to delete.
    *   **Response**: Returns a confirmation message.

#### Admin-Dataset Management

*   **`POST /dataset`**
    *   **Description**: Vectorizes a dataset and creates a new RAG system associated with it.
    *   **Request Body**:
        ```json
        {
            "dataset_id": "a_valid_uuid",
            "rag_name": "My New RAG System"
        }
        ```
    *   **Response**: Returns the created RAG system object.

*   **`GET /dataset`**
    *   **Description**: Lists all uploaded datasets, with an option to filter by their vectorized status.
    *   **Query Parameters**:
        *   `is_vectorized` (boolean, optional): Filter datasets by whether they have been vectorized.
    *   **Response**: Returns a list of dataset information objects.

*   **`DELETE /dataset`**
    *   **Description**: Deletes a dataset and its corresponding RAG system and vector store.
    *   **Query Parameters**:
        *   `dataset_id` (UUID): The ID of the dataset to delete.
    *   **Response**: Returns a confirmation message.

#### Admin-RAG System Management

*   **`GET /models`**
    *   **Description**: Lists available LLM models and RAG systems.
    *   **Response**: Returns an object containing lists of "simple", "user_rag", and available RAG systems.

*   **`GET /rag_system`**
    *   **Description**: Lists all available RAG systems.
    *   **Response**: Returns a list of RAG system objects.

*   **`PUT /rag_system`**
    *   **Description**: Changes the name of an existing RAG system.
    *   **Request Body**:
        ```json
        {
            "rag_system_id": "a_valid_uuid",
            "new_name": "Updated RAG System Name"
        }
        ```
    *   **Response**: Returns a confirmation message.

#### Admin-RAG System Access Management

*   **`POST /rag_access`**
    *   **Description**: Grants a user access to a specific RAG system.
    *   **Request Body**:
        ```json
        {
            "user_id": "a_valid_uuid",
            "rag_system_id": "a_valid_uuid"
        }
        ```
    *   **Response**: Returns a confirmation message.

*   **`GET /rag_access/users`**
    *   **Description**: Lists all users who have access to a specific RAG system.
    *   **Query Parameters**:
        *   `rag_system_id` (UUID): The ID of the RAG system.
    *   **Response**: Returns a list of user objects.

*   **`GET /rag_access/rag_systems`**
    *   **Description**: Lists all RAG systems that a specific user has access to.
    *   **Query Parameters**:
        *   `user_id` (UUID): The ID of the user.
    *   **Response**: Returns a list of RAG system objects.

*   **`DELETE /rag_access`**
    *   **Description**: Revokes a user's access to a specific RAG system.
    *   **Request Body**:
        ```json
        {
            "user_id": "a_valid_uuid",
            "rag_system_id": "a_valid_uuid"
        }
        ```
    *   **Response**: Returns a confirmation message.

## 6. License

```
Copyright 2025 Pouria Sarmasti
```
