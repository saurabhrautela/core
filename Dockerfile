FROM python:3.8-slim

LABEL \
Name=core \
Version=0.0.1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
PYTHONBREAKPOINT=0 \
GROUP=core \
APP_USER=core \
WORK_DIR=/home/core

ENV MEDIA_DIR=${WORK_DIR}/media \
LOG_DIR=${WORK_DIR}/log

ENV PATH=${PATH}:${WORK_DIR}/.local/bin

# Add user to run application
RUN groupadd -r ${GROUP} -g 1000 && \
useradd -r -u 1000 -g ${GROUP} -s /sbin/nologin -d ${WORK_DIR} ${APP_USER}

# Install python packages
COPY --chown=1000:1000 requirements.txt ${WORK_DIR}/requirements.txt

RUN buildDeps='gcc' \
    && apt-get update \
    && apt-get install -y ${buildDeps} libpq-dev \
    && su -s '/bin/sh' ${APP_USER} -c 'pip install --user -r ${WORK_DIR}/requirements.txt' \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge --auto-remove -y $buildDeps

COPY --chown=1000:1000 ./dev $WORK_DIR

# Create directories for media and logging
USER $APP_USER

RUN mkdir ${MEDIA_DIR} && \
    mkdir ${LOG_DIR}

WORKDIR $WORK_DIR

VOLUME $MEDIA_DIR
VOLUME $LOG_DIR

EXPOSE 8000
