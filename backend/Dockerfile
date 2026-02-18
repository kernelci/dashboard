# syntax=docker/dockerfile:1

# Create server docker image (all non-code dependencies)
FROM alpine:3.20 as backend-base

WORKDIR /

ENV POETRY_HOME=/opt/poetry
ENV PYTHONOPTIMIZE=${PYTHONOPTIMIZE:-2}
ENV PYTHONUNBUFFERED=${PYTHONUNBUFFERED:-1}

RUN apk update \
    && apk add --no-cache \
        python3 \
        python3-dev \
        gcc \
        libffi-dev \
        libc-dev \
        libpq-dev \
        postgresql \
        curl \
    && python3 -m venv $POETRY_HOME \
    && $POETRY_HOME/bin/pip install poetry==1.8.3 \
    && ln -s $POETRY_HOME/bin/poetry /bin/poetry

FROM backend-base as kernelci-django-backend
WORKDIR /backend
COPY . /backend

ARG INSTALL_DEV_DEPS=false
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
        poetry install --no-interaction; \
    else \
        poetry install --no-interaction --only main; \
    fi

ENV DJANGO_APP="kernelCI"

# Precompile Python modules
RUN PY_MAJMIN=`poetry run python -c "import sys; print('%s.%s'%sys.version_info[0:2])"` \
    PY_D=`poetry env info --path` \
    D="$PY_D $DJANGO_APP"; \
    echo "compile python $PY_MAJMIN byte code at $D"; \
    poetry run python -m compileall -q $D || exit 1;
