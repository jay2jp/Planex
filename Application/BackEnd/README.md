# Flask Application for Recommendation Chat

This Flask application provides a REST API endpoint that replicates the conversational chat functionality of the CLI interface in `Processor/queryPipeline/chat.py`.

## Features

- REST API endpoint for chat interactions
- Session management for maintaining conversation history
- Same recommendation pipeline logic as the CLI version
- CORS support for web integration

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the `Application/BackEnd` directory with the following:
   ```
   GOOGLE_API_KEY="your-google-api-key"
   DB_NAME=postgres
   DB_USER=postgres.USERNAME
   DB_PASSWORD="your-strong-password"
   DB_HOST=db.example.supabase.co
   DB_PORT=6543
   # Optional for connection pooling:
   DATABASE_POOLER_URL="postgresql://postgres.USERNAME:your-strong-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
   # Flask secret key (required for sessions):
   FLASK_SECRET_KEY="your-flask-secret-key"
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

## API Endpoints

### POST /chat
Send a chat message and receive a response.

**Request Body**:
```json
{
  "query": "Your natural language query"
}
```

**Response**:
```json
{
  "response": "AI's conversational response",
  "sources": [
    {
      "name": "Recommendation Name",
      "url": "https://source-url.com"
    }
  ]
}
```

### POST /reset
Reset the current chat session.

**Response**:
```json
{
  "message": "Chat session reset successfully"
}
```

### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

## Database Schema Requirements

The application requires the following PostgreSQL tables to function properly:

1. **recommendations**:
   ```sql
   CREATE TABLE recommendations (
       id SERIAL PRIMARY KEY,
       name TEXT,
       location TEXT,
       neighborhood TEXT,
       summary TEXT,
       quote TEXT,
       source_url TEXT UNIQUE,
       embedding VECTOR(1536)  -- Using pgvector extension
   );
   ```

2. **hashtags**:
   ```sql
   CREATE TABLE hashtags (
       id SERIAL PRIMARY KEY,
       tag TEXT UNIQUE
   );
   ```

3. **tags**:
   ```sql
   CREATE TABLE tags (
       id SERIAL PRIMARY KEY,
       tag TEXT UNIQUE
   );
   ```

4. **recommendation_hashtags**:
   ```sql
   CREATE TABLE recommendation_hashtags (
       recommendation_id INTEGER REFERENCES recommendations(id),
       hashtag_id INTEGER REFERENCES hashtags(id),
       PRIMARY KEY (recommendation_id, hashtag_id)
   );
   ```

5. **recommendation_tags**:
   ```sql
   CREATE TABLE recommendation_tags (
       recommendation_id INTEGER REFERENCES recommendations(id),
       tag_id INTEGER REFERENCES tags(id),
       PRIMARY KEY (recommendation_id, tag_id)
   );
   ```

6. **neighborhoods**:
   ```sql
   CREATE TABLE neighborhoods (
       id SERIAL PRIMARY KEY,
       name TEXT UNIQUE
   );
   ```

Note: The `embedding` column in the `recommendations` table uses the pgvector extension for PostgreSQL, which enables vector similarity search operations.