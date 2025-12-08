# Rewrite Studio

Small Streamlit app for rewriting and summarizing text with the OpenAI API.

The goal of this project is to show how I structure a simple AI feature:

- separate prompts, service layer, and UI
- keep API secrets in a local `.env`
- present a clean, minimal interface

## Features

- Rewrite text into a target tone:
  - Friendly
  - Confident
  - Concise
  - Playful
- Summarize text into:
  - Short summary
  - Medium summary
  - Detailed summary
- Streamlit front end with a two column layout
- Uses the official OpenAI Python SDK

## Getting started

Clone the repo:

```bash
git clone https://github.com/Dhudson-AI/rewrite-studio.git
cd rewrite-studio
