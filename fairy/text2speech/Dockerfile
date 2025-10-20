FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime

RUN apt-get update && apt-get install -y git ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN git clone https://github.com/resemble-ai/Chatterbox.git .
RUN pip install --upgrade pip
RUN pip install .
RUN python3 -m pip install --upgrade 'optree>=0.13.0'

# For faster start, download or clone models here if needed (optional)

ENTRYPOINT ["python", "main.py"]