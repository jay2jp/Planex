-- Database Schema for Planex Application

-- Enable pgvector extension (required for embedding similarity search)
CREATE EXTENSION IF NOT EXISTS vector;

-- Recommendations table
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

-- Hashtags table
CREATE TABLE hashtags (
    id SERIAL PRIMARY KEY,
    tag TEXT UNIQUE
);

-- Tags table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    tag TEXT UNIQUE
);

-- Recommendation-Hashtag relationship
CREATE TABLE recommendation_hashtags (
    recommendation_id INTEGER REFERENCES recommendations(id),
    hashtag_id INTEGER REFERENCES hashtags(id),
    PRIMARY KEY (recommendation_id, hashtag_id)
);

-- Recommendation-Tag relationship
CREATE TABLE recommendation_tags (
    recommendation_id INTEGER REFERENCES recommendations(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (recommendation_id, tag_id)
);

-- Neighborhoods table
CREATE TABLE neighborhoods (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

-- Indexes for performance
CREATE INDEX ON recommendations USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON recommendations (source_url);
CREATE INDEX ON hashtags (tag);
CREATE INDEX ON tags (tag);
CREATE INDEX ON neighborhoods (name);