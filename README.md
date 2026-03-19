# AI-Assisted Research Monitoring Prototype

## Overview

This project is a lightweight, end-to-end research monitoring tool designed to analyze online discourse using live Reddit data. It simulates the workflow of an internal analyst platform by transforming unstructured social media content into structured insights and actionable summaries.

The system ingests real-time Reddit discussions, preprocesses text data, classifies content into meaningful categories, detects emerging trends, and generates analyst-ready insights along with a downloadable report.

This prototype is intentionally designed to demonstrate practical data analysis, NLP processing, and insight generation in a clean, fast, and explainable pipeline.

---

## Key Features

### 1. Live Data Ingestion

- Scrapes real-time Reddit discussions using keyword-based search
- Supports optional subreddit filtering
- Configurable post limits for fast analysis

### 2. Text Preprocessing Pipeline

- Cleans raw unstructured text (URLs, punctuation, noise removal)
- Deduplicates posts
- Detects language
- Computes text length
- Extracts keywords
- Identifies simple named entities (heuristic-based)

### 3. Classification Engine

Posts are labeled using a rule-based classification system designed for analyst support (not moderation enforcement).

**Outputs include:**

- Relevance (relevant / not relevant)
- Topic classification (e.g., antisemitic rhetoric, misinformation, harassment)
- Sentiment (hostile / neutral / supportive)
- Concern level (low / medium / high)
- Short summary for each post

### 4. Trend Detection Engine

Transforms individual posts into patterns and signals.

**Includes:**

- Daily post volume tracking
- Topic distribution over time
- Concern level heatmap
- Keyword frequency analysis
- Subreddit concentration analysis
- Spike detection using rolling averages and z-score logic

### 5. Insight Generator

Automatically converts data into human-readable research insights.

**Generates:**

- Executive summary
- Top themes
- Source concentration analysis
- Monitoring recommendations
- Representative examples

### 6. Report Builder

- Generates a structured PDF report
- Includes key metrics, summaries, and insights
- Designed for stakeholder communication

---

## Application Workflow

The application is designed as a step-based pipeline:

1. **Scrape Data**
2. **Preprocess**
3. **Run Classification**
4. **Detect Trends**
5. **Generate Insights**
6. **Build Report**

This mirrors a real-world analyst workflow from raw data to final deliverable.

---

## User Interface

The application uses a structured layout:

### Sidebar (Control Panel)

- Date range selection
- Keyword / subreddit input
- Pipeline execution buttons
- Filters for topic, sentiment, and concern level

### Main Panel (Results)

Organized into six tabs:

1. Scraped Data
2. Preprocessing
3. Classification Engine
4. Trend Detection
5. Insight Generator
6. Report Builder

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/reddit-research-prototype.git
cd reddit-research-prototype
```
