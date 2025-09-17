# syntax=docker/dockerfile:1

# Create server docker image (all non-code dependencies)
FROM alpine:3.20 as backend-base

WORKDIR /

ENV POETRY_HOME=/opt/poetry

RUN apk update \
    && apk add --no-cache \
        python3 \
        python3-dev \
        gcc \
        libffi-dev \
        libc-dev \
        libpq-dev \
        postgresql \
    && python3 -m venv $POETRY_HOME \
    && $POETRY_HOME/bin/pip install poetry==1.8.3 \
    && ln -s $POETRY_HOME/bin/poetry /bin/poetry

FROM backend-base
COPY . /backend
COPY ./utils/docker/entrypoint.sh /entrypoint.sh
WORKDIR /backend

ARG INSTALL_DEV_DEPS=false
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
        poetry install --no-interaction; \
    else \
        poetry install --no-interaction --only main; \
    fi

ENV DJANGO_APP="kernelCI"

# Precompile Python modules
RUN O='0 1 2' \
        PY_MAJMIN=`poetry run python -c "import sys; print('%s.%s'%sys.version_info[0:2])"` \
        PY_D=`poetry env info --path` \
        D="$PY_D $DJANGO_APP"; \
        for N in $O; do \
            echo "compile python $PY_MAJMIN byte code at -O$N: $D"; \
            PYTHONOPTIMIZE=$N poetry run python -m compileall -q $D || exit 1; \
        done

EXPOSE 8000

ARG BACKEND_VOLUME_DIR
ENV BACKEND_VOLUME_DIR=${BACKEND_VOLUME_DIR}
RUN echo "Building with volume on: $BACKEND_VOLUME_DIR"
VOLUME ${BACKEND_VOLUME_DIR}

# gunicorn is added here but is run at the end of the entrypoint.
# This was done here such that we can run a custom command
# in the backend container without using gunicorn
CMD ["gunicorn", "kernelCI.wsgi:application", "--workers=5", "--forwarded-allow-ips=*", "--bind=0.0.0.0:8000", "--timeout=250"]
ENTRYPOINT ["/entrypoint.sh"]
