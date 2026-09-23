FROM python:3.13

WORKDIR /app

ENV TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=true DOCKER_CONTAINER=true

RUN apt-get update && apt-get install -y \
    ffmpeg

COPY requirements.txt ./
RUN pip install --root-user-action ignore --no-cache-dir -r requirements.txt


COPY . .

# Pre-download WhisperX models
RUN --mount=type=secret,id=hf_token,required=true \
    python -B api/download_models.py

ENV HF_HUB_OFFLINE=1

CMD [ "python", "api/app.py" ]
