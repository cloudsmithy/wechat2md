# 带 Python 3.12 与 uv 的精简镜像
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# 可选：更快的链接/更小兼容面的字节码编译
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# 仅拷贝依赖声明，充分利用构建缓存
COPY pyproject.toml uv.lock* ./

# 安装生产依赖到系统环境（无虚拟环境）
# --frozen：必须有锁文件且与依赖一致
# --no-dev：忽略 dev 依赖
# --system：装入系统 site-packages
RUN uv sync --frozen --no-dev --system

# 再拷贝源码
COPY . .

# 如有入口点可改用 `python -m your_pkg` 或 uvx 运行器
CMD ["python", "main.py"]
