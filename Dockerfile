# ========= builder：带构建工具 =========
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# 常见需要的系统依赖（按需裁剪/增减）
# - ca-certificates: 避免 TLS 失败
# - build-essential/pkg-config: 编译 C/C++ 扩展
# - libssl-dev/libffi-dev: 常见加密/ffi 库
# - python3-dev: 构建部分依赖需要头文件
# - cargo: 少数包需要 Rust（如某些加密/压缩库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates build-essential pkg-config libssl-dev libffi-dev python3-dev cargo \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 只拷依赖声明，最大化缓存命中
COPY pyproject.toml uv.lock* ./

# 用虚拟环境安装（不要 --system）
# --frozen：有 uv.lock 时保证可复现；如果你暂时没有锁文件，可以去掉 --frozen
# --no-dev：只装生产依赖；如需 dev 依赖删除此参数
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN uv sync --frozen --no-dev

# 再拷源码并把项目装进 venv
COPY . .
# 这一步可选：若需要根据源码再解析 extras/本地包
RUN uv sync --frozen --no-dev

# ========= runtime：精简运行镜像 =========
FROM python:3.12-slim AS runtime

# 证书（避免运行期请求失败）
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 从 builder 复制虚拟环境到 /opt/venv
COPY --from=builder /app/.venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# 复制应用源码
COPY . .

# 可选：非 root 运行更安全
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "app.py"]
