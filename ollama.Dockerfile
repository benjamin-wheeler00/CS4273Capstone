FROM docker.io/ollama/ollama

ARG ollama_model

RUN ollama serve & \
    sleep 1 && \
    ollama pull ${ollama_model}
