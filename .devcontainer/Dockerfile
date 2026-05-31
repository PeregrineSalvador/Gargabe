# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=0 \
    PIP_DEFAULT_TIMEOUT=300

# 1. 系统底层库（移除了所有干扰解析的行内注释）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    ffmpeg \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libglx0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libjpeg-dev \
    libpng-dev \
    xdotool \
    scrot \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 2. 彻底放弃官方源，直接用国内清华源，并强制无缓存安装
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple \
    opencv-python \
    mediapipe==0.10.9 \
    pyautogui \
    python-xlib \
    matplotlib \
    pyyaml

CMD ["python", "gesture_control.py"]