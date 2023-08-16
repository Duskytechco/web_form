FROM python:3.10-slim

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

RUN wget -qO chromium.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_113.0.5672.63-1_amd64.deb \
  && dpkg -i chromium.deb \
  && apt-get install -f -y \
  && rm -f chromium.deb


RUN wget -qO chromedriver.zip https://chromedriver.storage.googleapis.com/113.0.5672.63/chromedriver_linux64.zip \
  && unzip chromedriver.zip \
  && rm chromedriver.zip \
  && mv chromedriver /usr/bin/chromedriver \
  && chmod +x /usr/bin/chromedriver

COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "-u", "app.py"]
