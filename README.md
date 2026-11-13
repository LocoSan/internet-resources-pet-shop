# Магазин домашних животных

Работы 6 и 7, вариант 9. API и интерфейс каталога: виды, породы, животные.

Метки Git: `lab-06` — API; `lab-07` — API и клиент.

## Запуск

Команды из папки проекта (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py createsuperuser
.\.venv\Scripts\python.exe manage.py seed_catalog
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

При создании пользователя выберите логин и пароль. Команда `seed_catalog` заполняет каталог примерами.

## Swagger

Откройте [Swagger](http://127.0.0.1:8000/api/docs/). В `POST /api/token/` укажите логин и пароль. Скопируйте значение `access` без кавычек и вставьте в **Authorize**. После этого можно выполнять запросы к каталогу. Для получения нового access-токена есть `POST /api/token/refresh/`.

| Адрес | Данные |
| --- | --- |
| `/api/species/` | Виды |
| `/api/breeds/` | Породы |
| `/api/pets/` | Животные |

У каждой записи есть адрес с её номером, например `/api/pets/1/`. Списки показывают по пять записей; параметр `?page=2` открывает следующую страницу.

## Интерфейс

Оставьте Django запущенным. В другом окне PowerShell из папки проекта:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm dev
```

Нужны Node.js 22.13 или новее и pnpm 11. Откройте [клиент](http://localhost:5173/) и войдите тем же логином и паролем. Чтобы добавить животное в пустой каталог, сначала создайте вид и породу.

## Проверки

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py spectacular --validate --fail-on-warn --file "$env:TEMP\petshop-schema.yaml"
cd frontend
pnpm build
```
