#base
FROM python:3.11-slim
# FROM pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive

#working dir
WORKDIR /backend/

#copy
COPY requirements.txt .
COPY . .

#run
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir torch==2.6.0+cpu torchvision --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

#port
EXPOSE 8000

#command
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]