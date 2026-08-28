# syntax=docker/dockerfile:1.7

FROM node:22-bookworm-slim AS web-builder

WORKDIR /build/web
RUN corepack enable

COPY web/package.json web/pnpm-lock.yaml web/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY web/ ./
RUN mkdir -p .openai \
    && if [ ! -f .openai/hosting.json ]; then \
        printf '{"d1":null,"r2":null}\n' > .openai/hosting.json; \
    fi
ARG NEXT_PUBLIC_QIANCRAFT_API_URL=""
ENV NEXT_PUBLIC_QIANCRAFT_API_URL=${NEXT_PUBLIC_QIANCRAFT_API_URL}
RUN pnpm build


FROM node:22-bookworm-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/opt/venv/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    ALLOW_API_TXT_FALLBACK=false \
    QIANCRAFT_WORKBENCH_DIR=/app/data/runtime/workbench \
    QIANCRAFT_TOOL_WORKSPACE_DIR=/app/data/runtime/tool_workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        gettext-base \
        fonts-noto-cjk \
        nginx \
        openssl \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app/ ./app/
COPY data/ ./data/
RUN pip install --no-cache-dir .

COPY --from=web-builder /build/web ./web/
COPY deploy/nginx.conf.template /app/deploy/nginx.conf.template
COPY deploy/start-zeabur.sh /app/deploy/start-zeabur.sh
RUN sed -i 's/\r$//' /app/deploy/start-zeabur.sh \
    && chmod 0755 /app/deploy/start-zeabur.sh \
    && mkdir -p /app/data/runtime/workbench /app/data/runtime/tool_workspace /app/runtime/auth

EXPOSE 8080

CMD ["/app/deploy/start-zeabur.sh"]
