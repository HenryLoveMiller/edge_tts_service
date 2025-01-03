# Edge TTS Service

Edge TTS Service is a Flask-based web application that provides text-to-speech (TTS) functionality using the Edge TTS library. The generated audio files can be uploaded to a specified GitHub repository.

## Features

- Convert text to speech using various supported voices.
- Upload generated audio files to a specified GitHub repository.
- Configurable via environment variables.
- Supports both synchronous and asynchronous routes.

## Configuration

The application can be configured using environment variables. The following variables are required:

- `FLASK_ENV`: The environment in which the app is running (`development` or `production`).
- `SECRET_KEY`: A secret key for the Flask application.
- `TEMP_FILE_DIR`: Directory for storing temporary files.
- `BASE_URL`: Base URL for accessing generated files.
- `GITHUB_TOKEN`: GitHub token for accessing the repository.
- `GITHUB_REPO`: GitHub repository for storing audio files.
- `GITHUB_BRANCH`: Branch of the GitHub repository.
- `GITHUB_FOLDER`: Folder in the GitHub repository for storing audio files.

## Deployment Methods

### 1. Local Deployment

1. Clone the repository:

    ```sh
    git clone https://github.com/hillerliao/edge_tts_service.git
    cd edge_tts_service
    ```

2. Create a virtual environment and install dependencies:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. Create a `.env` file with the required environment variables:

    ```plaintext
    FLASK_ENV=development
    SECRET_KEY=your-secret-key
    TEMP_FILE_DIR=/tmp
    BASE_URL=http://localhost:5000
    GITHUB_TOKEN=your_github_token
    GITHUB_REPO=your_github_username/your_repository
    GITHUB_BRANCH=your-branch-name
    GITHUB_FOLDER=your-folder-name
    ```

4. Run the application:

    ```sh
    python run.py
    ```

### 2. Docker Deployment

1. Build the Docker image:

    ```sh
    docker build -t edge_tts .
    ```

2. Run the Docker container with environment variables:

    ```sh
    docker run -d --name edge_tts \
      -p 5002:5000 \
      -e FLASK_ENV=production \
      -e SECRET_KEY=your-secret-key \
      -e TEMP_FILE_DIR=/tmp \
      -e BASE_URL=http://localhost:5000 \
      -e GITHUB_TOKEN=your_github_token \
      -e GITHUB_REPO=your_github_username/your_repository \
      -e GITHUB_BRANCH=your-branch-name \
      -e GITHUB_FOLDER=your-folder-name \
      edge_tts
    ```

### 3. Docker Compose Deployment

1. Create a `docker-compose.yml` file with the following content:

    ```yaml
    version: '3.8'

    services:
      tts_service:
        build: .
        container_name: edge_tts
        restart: unless-stopped
        ports:
          - "5002:5000"
        volumes:
          - ./logs:/app/logs
        environment:
          FLASK_ENV: development
          SECRET_KEY: your-secret-key
          TEMP_FILE_DIR: /tmp
          BASE_URL: http://localhost:5000
          GITHUB_TOKEN: your_github_token
          GITHUB_REPO: your_github_username/your_repository
          GITHUB_BRANCH: your-branch-name
          GITHUB_FOLDER: your-folder-name
        command: gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
    ```

2. Run the Docker Compose setup:

    ```sh
    docker-compose up -d
    ```

## API Endpoints

### Get Supported Voices

- **URL**: `/voices`
- **Method**: `GET`
- **Description**: Retrieve a list of supported voices.

### Text to Speech

- **URL**: `/tts`
- **Method**: `GET`, `POST`
- **Description**: Convert text to speech and upload the generated audio file to GitHub.
- **Request Parameters (GET)**:
    - `text`: The text to convert to speech.
    - `voice`: The voice to use for the conversion.
    - `rate`: The rate of speech.
    - `volume`: The volume of speech.
    - `dl`: Download option (1 for direct download, 2 for player URL).
- **Request Body (POST)**:
    ```json
    {
        "text": "Hello, world!",
        "voice": "en-US-AriaNeural",
        "rate": "+0%",
        "volume": "+0%"
    }
    ```

## License

This project is licensed under the MIT License.