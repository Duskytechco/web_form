FROM python:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
  pkg-config \
  gcc \
  libcairo2-dev \
  wget \
  unzip \
  libgconf-2-4 \
  libnss3 \
  libxi6 \
  libatk-bridge2.0-0 \
  libgtk-3-0 \
  libgbm-dev \
  fonts-liberation \
  libasound2 \
  libcurl4 \
  libu2f-udev \
  libvulkan1 \
  xdg-utils

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "-u", "app.py"]
