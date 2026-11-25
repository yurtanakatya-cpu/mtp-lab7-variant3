# Лабораторная работа №7

Юрченко Екатерина Валентиновна, группа 221341, вариант 3.

Тема — работа с СУБД в Python. Проект представляет собой каталог книг на SQLite.

| Сложность | № | Задание |
| --- | --- | --- |
| Средняя | 3 | Выбрать данные из таблицы |
| Средняя | 5 | Удалить запись |
| Средняя | 9 | Экспортировать данные в CSV |
| Повышенная | 3 | Написать и применить миграции Alembic |
| Повышенная | 7 | Реализовать REST API на FastAPI и SQLAlchemy |

## Запуск

Нужны Python 3.12 и SQLite 3.35 или новее. В PowerShell из корня проекта:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

В Linux или macOS используйте `python3.12` для создания окружения
и `.venv/bin/python` для остальных команд. В выводе `alembic current`
ожидается `0002 (head)`.

По умолчанию Alembic, консольные команды и API используют `books.sqlite3`
в корне проекта. Чтобы работать с другой базой, задайте абсолютный путь
в переменной окружения `LAB7_DB_PATH` перед запуском всех трёх инструментов.
Родительский каталог файла должен существовать.

## Выборка, удаление и CSV

```powershell
.\.venv\Scripts\python.exe -m lab7_app add "Двенадцать стульев" "Ильф и Петров" --year 1928
.\.venv\Scripts\python.exe -m lab7_app list
New-Item -ItemType Directory -Force data | Out-Null
.\.venv\Scripts\python.exe -m lab7_app export data/catalog.csv
```

Команда `list` выполняет выборку в порядке ID. Команда `export` сохраняет
все записи в том же порядке вместе с заголовком `id,title,author,year`.
CSV записывается в UTF-8 с BOM, чтобы электронные таблицы распознавали
кириллицу. Пустой год становится пустой ячейкой. Для повторной выгрузки
укажите новое имя файла.

Подставьте ID, выданный командой `add`, и выполните `delete ID`. Например,
если ID равен 1:

```powershell
.\.venv\Scripts\python.exe -m lab7_app delete 1
.\.venv\Scripts\python.exe -m lab7_app list
```

Если ID отсутствует, команда сообщает об этом и возвращает код 1.
Операции выполняются через SQLAlchemy с параметрами запроса.

## Миграции Alembic

| Ревизия | Изменение |
| --- | --- |
| `0001` | Создаёт таблицу `books` с полями `id`, `title` и `author`. |
| `0002` | Добавляет необязательный `year`. У прежних записей год остаётся пустым. |

```powershell
.\.venv\Scripts\python.exe -m alembic history
.\.venv\Scripts\python.exe -m alembic check
.\.venv\Scripts\python.exe -m unittest tests.test_migrations -v
```

Последняя команда создаёт отдельную временную базу, применяет `0001`,
добавляет строку и обновляется до `0002`. Тест проверяет данные и
ограничение на год, откатывает миграцию и убеждается, что книга осталась
в таблице. При откате `0002` значения поля `year` удаляются.
Создание и изменение схемы выполняет Alembic.

## REST API

После миграций запустите Uvicorn:

```powershell
.\.venv\Scripts\python.exe -m uvicorn lab7_app.api:app --host 127.0.0.1 --port 8000
```

Откройте [Swagger UI](http://127.0.0.1:8000/docs). Выберите
`POST /books`, нажмите **Try it out**, вставьте JSON и нажмите **Execute**:

```json
{
  "title": "Капитанская дочка",
  "author": "Александр Пушкин",
  "year": 1836
}
```

Используйте полученный ID в запросах на просмотр, замену и удаление.
Добавленная через API книга также появится в консольной выборке и CSV.

| Запрос | Результат |
| --- | --- |
| `POST /books` | Записывает книгу, возвращает `201` и адрес записи в `Location`. |
| `GET /books?offset=0&limit=50` | Возвращает список в порядке ID. Максимальный размер страницы — 100 записей. |
| `GET /books/{id}` | Возвращает книгу или `404`. |
| `PUT /books/{id}` | Заменяет название, автора и год. Если год пропущен, сохраняет `null`. |
| `DELETE /books/{id}` | Удаляет запись, возвращает `204` без тела или `404`. |

Название и автор обязательны. Год должен быть целым числом от 1 до 2100
или `null`. Некорректное тело запроса возвращает `422`. Для каждого
запроса открывается отдельная сессия SQLAlchemy.

## Проверки проекта

```powershell
.\.venv\Scripts\python.exe -m unittest discover -v
```

Семь тестов используют временные файлы SQLite. Они проверяют миграции
с данными, выборку и удаление, CSV с кириллицей и кавычками, CRUD,
валидацию, разбиение списка на страницы и повторное чтение базы.
Отдельно проверены реальные HTTP-запросы через Uvicorn и экспорт записи,
созданной через API.

[Документация Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html) ·
[SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) ·
[FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/)
