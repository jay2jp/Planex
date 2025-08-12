# Planex Application

This repository contains the Planex application, which provides local recommendations through AI-powered analysis of social media content.

## Components

### ApifyInstaGetter
Tools for retrieving Instagram content using Apify.

### ApifyLinkGetter
Tools for retrieving TikTok content using Apify.

### Processor
Contains the query pipeline that processes user queries and generates recommendations:
- `queryPipeline` - The main recommendation engine with CLI interface
- Other processing scripts

### Application/BackEnd
Flask web application that exposes the recommendation engine through a REST API with session support.

## Getting Started

1. Install dependencies for each component:
   ```bash
   # For the Processor/queryPipeline
   pip install -r Processor/requirements.txt
   
   # For the Application/BackEnd
   pip install -r Application/BackEnd/requirements.txt
   ```

2. Set up environment variables in each component's directory (see `.env.example` files)

3. Run the applications:
   ```bash
   # CLI version
   python Processor/queryPipeline/chat.py
   
   # Flask API version
   python Application/BackEnd/app.py
   ```

## Database Schema

The application requires a PostgreSQL database with the following tables:
- recommendations
- hashtags
- tags
- recommendation_hashtags
- recommendation_tags
- neighborhoods

See `Application/BackEnd/README.md` for detailed schema information.