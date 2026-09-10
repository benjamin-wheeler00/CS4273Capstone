FROM python:3.13

WORKDIR /app

ENV TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=true

RUN apt-get update && apt-get install -y \
    ffmpeg

COPY requirements.txt ./
RUN pip install --root-user-action ignore --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "api/app.py" ]
