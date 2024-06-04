## 정보

- Python version 3.10.12
- FastAPI
- Alembic
- SQLAlchemy + SQLModel

## 환경세팅

`**.env**`를 프로젝트 루트에 만들고 `**.env.example**`를 바탕으로 값을 넣어주세요.
(실제 값은 관리자에게 문의해주세요.)

## 로컬커멘드

- Install python package requirements

  ```sh
  cd server/app
  pip install -r requirements.txt
  ```

## 1. 서버 RUN

도커커맨드

```sh
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
```

make파일

```sh
make run-dev-build
```

## 2. DB 생성

1. postgres docker container 엑세스

2. root user 로그인 `postgres`

   ```sh
   psql -U postgres;
   ```

3. database 생성, (Here, `jin`)

   ```sh
   create database jin;
   ```

## 3. 테이블 생성

도커커맨드

```sh
docker compose -f docker-compose.dev.yml exec server bash -c 'cd /app/app && python -m alembic revision --autogenerate'
docker compose -f docker-compose.dev.yml exec server bash -c 'cd /app/app && python -m alembic upgrade head'
```

MAKE 파일

```sh
make add-dev-migration
```
