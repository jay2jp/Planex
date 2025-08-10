# Advanced Recommendation Pipeline

This project implements a multi-step pipeline to provide users with synthesized, context-aware answers to their queries. It goes beyond a simple database lookup by expanding the user's query, retrieving a diverse set of relevant recommendations, and synthesizing the findings into a helpful, human-readable text answer complete with source links.

## Features

- **Query Expansion**: Uses a generative model to expand a simple user query into multiple, more specific queries.
- **Multi-Query Execution**: Executes a vector similarity search for each expanded query to gather a wide range of recommendations.
- **Candidate Pooling and Deduplication**: Aggregates results from all queries and removes duplicates to create a unique set of candidates.
- **Answer Synthesis**: Uses a powerful generative model to create a conversational, helpful answer from the candidate recommendations.
- **Citations**: Provides a list of source URLs for all aformentioned recommendations.

## Requirements

- Python 3.6+
- The dependencies listed in `requirements.txt` (install with `pip install -r requirements.txt`)

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r Processor/requirements.txt
   ```

2. **Create a `.env` file** in the `Processor/queryPipeline` directory with the following environment variables:
   ```
   GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
   DATABASE_POOLER_URL="YOUR_DATABASE_POOLER_URL"
   # Or, if not using a pooler:
   DB_NAME="YOUR_DB_NAME"
   DB_USER="YOUR_DB_USER"
   DB_PASSWORD="YOUR_DB_PASSWORD"
   DB_HOST="YOUR_DB_HOST"
   DB_PORT="YOUR_DB_PORT"
   ```

## Usage

To run the pipeline, use the following command:

```bash
python3 Processor/queryPipeline/main.py "Your natural language query"
```

For example:

```bash
python3 Processor/queryPipeline/main.py "Where can I find a good, cheap slice of pizza?"
```
