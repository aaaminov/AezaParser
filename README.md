# AezaParser

Приложение помогает подобрать виртуальный сервер по его характеристикам, с сервиса [Aeza](aeza.net).

Сайт предоставляет несколько видов серверов и тарифов, различающихся по логике работы, цене и задачам, под которые они предназначены. 

**Shared** - вид серверов, использующий программное разделение мощностей физического серверного оборудования с выделением клиенту оплаченных им мощностей. Для лучшего понимания можно сравнить с использованием вашего ПК сразу несколькими пользователями с их личными учетными записями.

**Promo** - подвид "Shared", для нетребовательных задач: хостинг небольших лэндингов, одиночных страниц, ботов или тестовых приложений; с урезанной тех. поддержкой. Подойдёт для теста собственного кода и проверки его работоспособности и безопасности до переноса на полноценный тариф.

**Dedicated** - более производительный вид серверов, использующий физическое разделение серверных мощностей, которые и являются причиной более высокой стоимости. При использовании клиент получает в личное владение физическую часть характеристик серверного оборудования.

Также на отдельных страницах сервиса доступны **Hi-CPU** и **выделенные** сервера, для требовательных задач. Они в поиске **не учитываются**.

Приложение поставил на хостинг по адресу: http://150.241.64.121:7777/ (уже нет)

## Технологии

- Язык программирования: Python 3.12.2
- Библиотеки:
  - `Flask` для разработки веб-интерфейса;
  - `Selenium` для автоматизации действий веб-браузера при парсинге, так как тарифы подгружаются на сайт динамически;
  - `WebdriverManager` для имитации браузера;
  - `SQLAlchemy` это расширение для Flask, для работы с базой данных.
- Docker: Для развёртывания приложения в контейнерах.

## Запуск

Для запуска нужен установленный [Docker](https://docs.docker.com/get-started/get-docker/)

Для сборки и запуска проекта используются команды:

```bash
docker build -t aeza-parser .
docker compose up --build
```

или готовым скриптом:

```bash
./build.sh
```

Затем сайт доступен локально по адресу: http://172.18.0.2:7777/

## Сайт

На исходной странице [сайта](https://aeza.net/ru/virtual-servers) выбирается локация, затем выводятся доступные типы серверов и тарифы с описанием характеристик.

Здесь же по характеристикам сервера выводятся типы серверов с локациями и соответствующими тарифами.

Вы можете настроить фильтры:

- Тип сервера (`Promo`, `Shared`, `Dedicated`).
- Минимальное количество ядер.
- Минимальный объем оперативной памяти.
- Минимальный объем дискового пространства.

![image](https://github.com/user-attachments/assets/2f7df9a4-f722-45c6-ae4e-ef803cf621fc)
