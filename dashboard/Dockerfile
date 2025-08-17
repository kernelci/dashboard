# Stage 1: Build the dashboard assets
FROM node:22.3-alpine AS builder

WORKDIR /dashboard

COPY dashboard/package.json dashboard/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

COPY dashboard/. ./

RUN pnpm build

# Stage 2: Copy the static files from the builder stage
FROM alpine:3.20

VOLUME ["/data/static/"]

RUN apk add --no-cache rsync

COPY --from=builder /dashboard/dist /files

CMD rsync -azvi --checksum --exclude='*.map' /files/ /data/static/
