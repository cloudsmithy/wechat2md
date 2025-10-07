# 使用带 uv 的官方 Python 镜像
FROM ghcr.io/astral-sh/uv:python3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 使用 uv 安装依赖（速度比 pip 快得多）
RUN uv pip install --system --no-cache -r requirements.txt

# 复制项目代码
COPY . .

# 启动命令
CMD ["python", "app.py"]
