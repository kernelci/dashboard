# Stage 1: Build the dashboard assets
FROM node:22.3-alpine AS builder

WORKDIR /dashboard

COPY dashboard/package.json dashboard/pnpm-lock.yaml ./
RUN npm install -g pnpm@10.33.3 && pnpm install --frozen-lockfile

COPY dashboard/. ./

COPY PRIVACY.md ../PRIVACY.md

ARG DASHBOARD_VERSION
ENV VITE_DASHBOARD_VERSION=$DASHBOARD_VERSION

RUN pnpm build

# Stage 2: Copy the static files from the builder stage
FROM alpine:3.20

VOLUME ["/data/static/"]

RUN apk add --no-cache rsync

COPY --from=builder /dashboard/dist /files

CMD rsync -azvi --checksum --exclude='*.map' /files/ /data/static/
