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
    QIANCRAFT_CONTINUOUS_COLLECTION=true \
    QIANCRAFT_CULTURE_WATCH_MINUTES=360 \
    QIANCRAFT_MARKET_REFRESH_MINUTES=240 \
    QIANCRAFT_DAILY_DESIGN_ENABLED=true \
    QIANCRAFT_DAILY_DESIGN_HOUR=7 \
    QIANCRAFT_DAILY_DESIGN_MINUTE=0 \
    QIANCRAFT_RUNTIME_ROOT=/app/data/runtime \
    QIANCRAFT_WORKBENCH_DIR=/app/data/runtime/workbench \
    QIANCRAFT_TOOL_WORKSPACE_DIR=/app/data/runtime/tool_workspace \
    QIANCRAFT_BROWSER_SESSION_ENABLED=true \
    QIANCRAFT_BROWSER_PROFILE_DIR=/app/data/runtime/browser-profile \
    QIANCRAFT_BROWSER_AUTH_URL=/browser-auth/vnc.html?autoconnect=1&resize=scale&path=browser-auth/websockify \
    GPT_RESEARCHER_PATH=/app/researcher_agent/gpt-researcher-main \
    LIGHTRAG_PATH=/app/local_culture/LightRAG-main \
    LIGHTRAG_STORAGE_DIR=/app/data/runtime/lightrag_storage \
    MEDIACRAWLER_PATH=/app/market-intel_agent/MediaCrawler-main \
    MEDIACRAWLER_PYTHON=/opt/mediacrawler-venv/bin/python \
    MEDIACRAWLER_LIVE_ENABLED=true \
    MEDIACRAWLER_PLATFORMS=xhs,bili,wb \
    MEDIACRAWLER_LOGIN_METHOD=cdp \
    MEDIACRAWLER_CDP_PORT=9222 \
    MEDIACRAWLER_CDP_CONNECT_EXISTING=true \
    MEDIACRAWLER_HEADLESS=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        chromium \
        dbus-x11 \
        gettext-base \
        fonts-liberation \
        fonts-noto-cjk \
        fonts-noto-color-emoji \
        gosu \
        libgl1 \
        libglib2.0-0 \
        libmagic1 \
        nginx \
        novnc \
        openbox \
        openssl \
        python3 \
        python3-pip \
        python3-venv \
        websockify \
        x11vnc \
        xauth \
        xvfb \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv \
    && python3 -m venv /opt/mediacrawler-venv

WORKDIR /app

COPY local_culture/LightRAG-main/ ./local_culture/LightRAG-main/
COPY researcher_agent/gpt-researcher-main/ ./researcher_agent/gpt-researcher-main/
RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel \
    && /opt/venv/bin/pip install --no-cache-dir \
        -e /app/local_culture/LightRAG-main \
        -e /app/researcher_agent/gpt-researcher-main \
    && /opt/venv/bin/python -c "import gpt_researcher, lightrag"

COPY market-intel_agent/MediaCrawler-main/requirements.txt /tmp/mediacrawler-requirements.txt
COPY deploy/mediacrawler-runtime-overrides.txt /tmp/mediacrawler-runtime-overrides.txt
RUN /opt/mediacrawler-venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel \
    && /opt/mediacrawler-venv/bin/pip install --no-cache-dir \
        -r /tmp/mediacrawler-requirements.txt \
    && /opt/mediacrawler-venv/bin/pip install --no-cache-dir --upgrade \
        -r /tmp/mediacrawler-runtime-overrides.txt \
    && /opt/mediacrawler-venv/bin/pip uninstall --yes fastapi starlette uvicorn \
    && /opt/mediacrawler-venv/bin/pip check \
    && /opt/mediacrawler-venv/bin/python -c "import cv2, pandas, playwright, pydantic"
COPY market-intel_agent/MediaCrawler-main/ ./market-intel_agent/MediaCrawler-main/
RUN cd /app/market-intel_agent/MediaCrawler-main \
    && PYTHONPATH=. /opt/mediacrawler-venv/bin/python -c \
        "import httpx; from tools.cdp_browser import CDPBrowserManager; import main" \
    && touch /opt/mediacrawler-venv/.qiancraft-runtime-ready

COPY pyproject.toml README.md ./
COPY app/ ./app/
COPY scripts/runtime_snapshot.py ./scripts/runtime_snapshot.py
COPY scripts/probe_market_platforms.py ./scripts/probe_market_platforms.py
COPY data/ ./data/
RUN pip install --no-cache-dir --no-deps . \
    && touch /opt/venv/.qiancraft-research-runtime-ready

COPY --from=web-builder /build/web ./web/
COPY deploy/nginx.conf.template /app/deploy/nginx.conf.template
COPY deploy/start-zeabur.sh /app/deploy/start-zeabur.sh
RUN sed -i 's/\r$//' /app/deploy/start-zeabur.sh \
    && chmod 0755 /app/deploy/start-zeabur.sh \
    && mkdir -p \
        /app/data/runtime/browser-profile \
        /app/data/runtime/lightrag_storage \
        /app/data/runtime/workbench \
        /app/data/runtime/tool_workspace/studio \
        /app/runtime/auth

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD node -e "fetch('http://127.0.0.1:8787/api/health').then((response) => { if (!response.ok) process.exit(1) }).catch(() => process.exit(1))"

CMD ["/app/deploy/start-zeabur.sh"]
