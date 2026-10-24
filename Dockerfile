FROM node:20-bookworm-slim AS build

ENV NEXT_TELEMETRY_DISABLED=1
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/venv

COPY requirements.txt package.json package-lock.json ./
RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && npm ci

COPY . .
RUN npm run build


FROM node:20-bookworm-slim AS production

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PYTHONUNBUFFERED=1 \
    PYTHON_BIN=/opt/venv/bin/python \
    PATH=/opt/venv/bin:$PATH \
    PORT=3000
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /opt/venv /opt/venv
COPY --from=build /app /app

EXPOSE 3000
CMD ["./scripts/start-production.sh"]
