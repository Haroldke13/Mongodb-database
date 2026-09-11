# syntax=docker/dockerfile:1
###############################################################################
# Mongodb-database — Flask + PyMongo to-do demo
#
# Build:  docker build -t todo:latest .
# Run:    see DEPLOY.md
#
# This app has NO authentication of any kind. Anyone who can reach it can read,
# create and delete every to-do. Put Cloudflare Access in front of the hostname
# or do not publish it. DEPLOY.md section 5.
###############################################################################

FROM python:3.12.3-slim-bookworm AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /build
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install -r requirements.txt

FROM python:3.12.3-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=5762

COPY --from=builder /opt/venv /opt/venv

RUN useradd --system --create-home --uid 10006 --shell /usr/sbin/nologin appuser

WORKDIR /app
COPY --chown=root:root . /app

USER appuser

EXPOSE 5762

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:5762/healthz', timeout=4).status == 200 else 1)"

# Tiny app, all state in MongoDB, nothing written to disk: safe with --read-only.
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5762", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "30", \
     "--graceful-timeout", "15", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "deploy_wsgi:app"]
