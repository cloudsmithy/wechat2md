FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# 只拷依赖声明以利用缓存
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --system || uv sync --no-dev --system

# 再拷源码
COPY . .

CMD ["python", "app.py"]
