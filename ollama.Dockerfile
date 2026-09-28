FROM docker.io/ollama/ollama

ARG ollama_model

RUN ollama serve & \
    ollama pull ${ollama_model}
