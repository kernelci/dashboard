# syntax=docker/dockerfile:1

# Build stage: Install dependencies and build the application
FROM alpine:3.20 as builder
WORKDIR /backend

RUN apk update && \
    apk add --no-cache \
        python3 \
        python3-dev \
        gcc \
        libffi-dev \
        libc-dev \
        libpq-dev \
        curl

COPY pyproject.toml poetry.lock /backend/

ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_IN_PROJECT=1

RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==1.8.3

ARG INSTALL_DEV_DEPS=false
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
        $POETRY_HOME/bin/poetry install --no-interaction; \
    else \
        $POETRY_HOME/bin/poetry install --no-interaction --only main; \
    fi

# Copy application code
COPY . /backend/

# Precompile Python modules
RUN O='0 1 2' \
        PY_MAJMIN=`$POETRY_HOME/bin/poetry run python -c "import sys; print('%s.%s'%sys.version_info[0:2])"`  \
        PY_D=`$POETRY_HOME/bin/poetry env info --path` \
        D="$PY_D kernelCI"; \
        for N in $O; do \
            echo "compile python $PY_MAJMIN byte code at -O$N: $D"; \
            PYTHONOPTIMIZE=$N $POETRY_HOME/bin/poetry run python -m compileall -q $D || exit 1; \
        done

# Runtime stage: Create a clean image with only runtime dependencies
FROM alpine:3.20 as app
WORKDIR /backend

# Install only runtime dependencies (no build tools)
RUN apk update && \
    apk add --no-cache \
        python3 \
        libpq \
        postgresql-client \
        curl

COPY --from=builder /opt/poetry /opt/poetry
COPY --from=builder /backend/.venv /backend/.venv

ENV PATH="/backend/.venv/bin:/opt/poetry/bin:$PATH"

COPY --from=builder /backend /backend
COPY --from=builder /backend/utils/docker/entrypoint.sh /entrypoint.sh

ARG BACKEND_VOLUME_DIR
ENV BACKEND_VOLUME_DIR=${BACKEND_VOLUME_DIR}
RUN echo "Building with volume on: $BACKEND_VOLUME_DIR"
VOLUME ${BACKEND_VOLUME_DIR}

# Expose both application and metrics ports
EXPOSE 8000 8001

# gunicorn is added here but is run at the end of the entrypoint.
# This was done here such that we can run a custom command
# in the backend container without using gunicorn
CMD ["gunicorn", "kernelCI.wsgi:application", "--workers=5", "--forwarded-allow-ips=*", "--bind=0.0.0.0:8000", "--timeout=250"]
ENTRYPOINT ["/entrypoint.sh"]
