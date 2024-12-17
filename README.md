# How to run

```shell
    cp .env.sample .env 
    && chmod 777 dc.sh 
    && chmod 777 migrate-db.sh
```

```shell
  ./dc.sh up -d
```

```shell
  ./migrate-db.sh
```

## Swagger

http://localhost:8000/api/v1/docs

## Redoc

http://localhost:8000/api/v1/redoc

## Check html display

http://localhost:8000/api/v1/checks/{id}