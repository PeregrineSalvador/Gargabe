# syntax=docker/dockerfile:1.6
FROM python:3.11-slim

# 1. 基础环境（安装系统库，摄像头/GUI 相关运行时）
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=300
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    wget \
    ffmpeg \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libgles2 \
    libglib2.0-0 \
    libgtk2.0-0 \
    libjpeg-dev \
    libpng-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# 2. 升级 pip 并准备安装 Python 依赖（不包含 pytorch/cuda）
RUN python -m pip install --upgrade pip setuptools wheel

# 3. 升级 pip 并强制卸载残缺的 mediapipe，从清华源安装纯净版本
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip uninstall mediapipe -y && \
    python -m pip install --no-cache-dir mediapipe==0.10.9 -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    python -m pip install --no-cache-dir pyautogui matplotlib pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple

# 4. 工作目录
WORKDIR /workspace

# 5. 默认命令（可覆盖）
CMD ["python", "gesture_recognition_cam.py"]