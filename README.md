# Проект Меню ресторана: 
[![Test Suite](https://github.com/alexpro2022/restaurant_menu-FastAPI/actions/workflows/main.yml/badge.svg)](https://github.com/alexpro2022/restaurant_menu-FastAPI/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/alexpro2022/restaurant_menu-FastAPI/branch/main/graph/badge.svg?token=iGgRPVwiiZ)](https://codecov.io/gh/alexpro2022/restaurant_menu-FastAPI)

### Simple RESTful API using FastAPI for a restaurant menu application

[Тестовое задание](https://ylab.zenclass.ru/student/courses/3befc192-e777-4736-8325-4cd8d28c4f07/tasks/b97560d4-4130-478e-ae3a-b98b2e896a38)

<br>

## Оглавление
- [Технологии](#технологии)
- [Описание работы](#описание-работы)
- [Установка приложения](#установка-приложения)
- [Запуск тестов](#запуск-тестов)
- [Запуск приложения](#запуск-приложения)
- [Удаление приложения](#удаление-приложения)
- [Автор](#автор)

<br>

## Технологии
<details><summary>Подробнее</summary><br>

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/-FastAPI-464646?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/-Pydantic-464646?logo=Pydantic)](https://docs.pydantic.dev/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?logo=PostgreSQL)](https://www.postgresql.org/)
[![asyncpg](https://img.shields.io/badge/-asyncpg-464646?logo=PostgreSQL)](https://pypi.org/project/asyncpg/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-v2.0-blue?logo=sqlalchemy)](https://www.sqlalchemy.org/)
[![Alembic](https://img.shields.io/badge/-Alembic-464646?logo=alembic)](https://alembic.sqlalchemy.org/en/latest/)
[![docker_compose](https://img.shields.io/badge/-Docker%20Compose-464646?logo=docker)](https://docs.docker.com/compose/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?logo=NGINX)](https://nginx.org/ru/)
<!--
[![Uvicorn](https://img.shields.io/badge/-Uvicorn-464646?logo=Uvicorn)](https://www.uvicorn.org/)
[![Pytest](https://img.shields.io/badge/-Pytest-464646?logo=Pytest)](https://docs.pytest.org/en/latest/)
[![Pytest-asyncio](https://img.shields.io/badge/-Pytest--asyncio-464646?logo=Pytest-asyncio)](https://pypi.org/project/pytest-asyncio/)
[![docker_hub](https://img.shields.io/badge/-Docker_Hub-464646?logo=docker)](https://hub.docker.com/)-->

[⬆️Оглавление](#оглавление)

</details>

<br>

## Описание работы

Даны 3 сущности:
  - Меню, 
  - Подменю, 
  - Блюдо.

Зависимости:
  - У меню есть подменю, которые к нему привязаны.
  - У подменю есть блюда, которые к нему привязаны.

Условия:
  - Блюдо не может быть привязано напрямую к меню, минуя подменю.
  - Блюдо не может находиться в 2-х подменю одновременно.
  - Подменю не может находиться в 2-х меню одновременно.
  - Если удалить меню, должны удалиться все подменю и блюда этого меню.
  - Если удалить подменю, должны удалиться все блюда этого подменю.
  - Цены блюд выводить с округлением до 2 знаков после запятой.
  - Во время выдачи списка меню, для каждого меню добавлять кол-во подменю и блюд в этом меню.
  - Во время выдачи списка подменю, для каждого подменю добавлять кол-во блюд в этом подменю.

Swagger позволяет осуществлять http-запросы к работающему сервису, тем самым можно управлять этими в рамках политики сервиса 

<!--(указано в Swagger для каждого запроса).

Неавторизованные пользователи могут получать доступ либо ко всем постам, либо к конкретному посту. 

Авторизованный пользователь дополнительно может создавать посты, редактировать и удалять свои посты (админ имеет права доступа к любым постам), ставить лайки и дислайки для любых постов, кроме своих. Для доступа к этим функциям необходимо авторизоваться в Swagger, используя: 
  - либо учетные данные из **.env**-файла (этот пользователь с правами админа создается программно при запуске приложения)
  - либо учетные данные нового зарегистрированного пользователя - зарегистрироваться можно через эндпоинт /auth/register  в Swagger:

Авторизация:
 1. Нажмите:
    - на символ замка в строке любого эндпоинта или 
    - на кнопку `Authorize` в верхней части Swagger. 
     Появится окно для ввода логина и пароля.

 2. Введите учетные данные в поля формы: 
    - в поле `username` — адрес почты (например значение переменной окружения `ADMIN_EMAIL`), 
    - в поле `password` — пароль (например значение переменной окружения `ADMIN_PASSWORD`). 
    
    В выпадающем списке `Client credentials location` оставьте значение `Authorization header`, 
    остальные два поля оставьте пустыми; нажмите кнопку `Authorize`. 
Если данные были введены правильно, и таблица в БД существует — появится окно с подтверждением авторизации, нажмите `Close`.
Чтобы разлогиниться — перезагрузите страницу.-->

[⬆️Оглавление](#оглавление)

<br>

## Установка приложения:

<details><summary>Предварительные условия</summary>
 
Предполагается, что пользователь установил [Docker](https://docs.docker.com/engine/install/) и [Docker Compose](https://docs.docker.com/compose/install/) на локальной машине. Проверить наличие можно выполнив команды:

```bash
docker --version && docker-compose --version
```
<h1></h1></details>

<!--details><summary>Локальный запуск</summary--> 
<br>

Клонируйте репозиторий с GitHub и введите данные для переменных окружения (значения даны для примера, но их можно оставить):

```bash
git clone https://github.com/alexpro2022/restaurant_menu-FastAPI.git && \
cd restaurant_menu-FastAPI && \
cp env_example .env && \
nano .env
```

[⬆️Оглавление](#оглавление)

<br>

## Запуск тестов:

Из корневой директории проекта выполните команду:
```bash
docker build -f test.Dockerfile -t restaurant_menu_tests . && \
docker run --name tests restaurant_menu_tests && \
docker container rm tests && \
docker rmi restaurant_menu_tests
```

[⬆️Оглавление](#оглавление)


<br>

## Запуск приложения:

1. Из корневой директории проекта выполните команду:
```bash
docker compose -f infra/local/docker-compose.yml up -d --build
```
Проект будет развернут в трех docker-контейнерах (db, web, nginx) по адресу http://127.0.0.1:8000.

Администрирование приложения может быть осуществлено через Swagger доступный по адресу http://127.0.0.1:8000/docs .

2. Остановить docker и удалить контейнеры можно командой из корневой директории проекта:
```bash
docker compose -f infra/local/docker-compose.yml down
```
Если также необходимо удалить том базы данных:
```bash
docker compose -f infra/local/docker-compose.yml down -v
```

[⬆️Оглавление](#оглавление)

<br>

## Удаление приложения:
Из корневой директории проекта выполните команду:
```bash
cd .. && rm -fr restaurant_menu-FastAPI
```
  
[⬆️Оглавление](#оглавление)

<br>

## Автор:
[Aleksei Proskuriakov](https://github.com/alexpro2022)

[⬆️В начало](#Проект-Меню-ресторана)
