FROM docker.io/ollama/ollama

ARG ollama_model

RUN ollama pull ${ollama_model}
