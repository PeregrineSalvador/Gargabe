FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# 1. 基础环境
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    python3.9-distutils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 2. Python 别名
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1

# 3. PyTorch（CUDA 11.8）
RUN pip install --no-cache-dir \
    torch==2.5.1+cu118 \
    torchvision==0.20.1+cu118 \
    torchaudio==2.5.1+cu118 \
    --index-url https://download.pytorch.org/whl/cu118

# 4. 项目依赖
RUN pip install --no-cache-dir \
    ultralytics==8.4.56 \
    opencv-python-headless \
    matplotlib \
    pyyaml

# 5. 工作目录
WORKDIR /workspace

# 6. 拷贝代码（训练 / 推理）


# 7. 默认命令（可覆盖）
CMD ["python", "train.py"]