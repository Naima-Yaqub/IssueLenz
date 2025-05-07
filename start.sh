#!/bin/bash

# Ensure the app waits for Ollama to be available
echo "Waiting for Ollama to start..."
until curl -s http://ollama:11434/api/tags | grep -q 'models'; do
  sleep 2
done

echo "Ollama is up! Checking available models..."

# Auto-pull the model if none exist
if [ "$(curl -s http://ollama:11434/api/tags)" = '{"models":[]}' ]; then
  echo "No models found. Pulling deepseek-r1:1.5b..."
  ollama pull deepseek-r1:1.5b
fi

# Start the Streamlit app
streamlit run /app/issues_summarizer/locallama.py --server.port 8501 --server.address 0.0.0.0
