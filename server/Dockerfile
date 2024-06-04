FROM python:3.10-slim as base

ENV PYROOT /pyroot
ENV PYTHONUSERBASE $PYROOT

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_USER=1

ENV TZ=Asia/Seoul

FROM base AS builder

ENV PIPENV_VENV_IN_PROJECT=1

RUN pip install --user pipenv
COPY ./app/Pipfile.lock ./app/Pipfile /usr/src/

WORKDIR /usr/src

RUN $PYROOT/bin/pipenv sync

FROM base AS runtime

COPY --from=builder /usr/src/.venv $PYROOT/.venv

ENV PATH="$PYROOT/.venv/bin:$PATH"

RUN apt-get update && apt-get -y install libgl1-mesa-glx libglib2.0-0

WORKDIR /app

COPY . .

RUN chmod +x /app/entrypoint_server.sh
EXPOSE 80

ENTRYPOINT [ "sh", "/app/entrypoint_server.sh" ]