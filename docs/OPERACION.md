# Operacion

## Servicios Docker

`docker-compose.yml` define:

| Servicio | Contenedor | Puerto |
| --- | --- | --- |
| API Django | `nurax_api` | `8000` |
| PostgreSQL | `nurax_db` | `5432` |

El comando del contenedor API ejecuta migraciones, `init_db.py` y luego levanta Django:

```bash
python manage.py migrate && python init_db.py && python manage.py runserver 0.0.0.0:8000
```

## Variables de Entorno

Archivos usados:

- `.env`
- `config/postgres.env`

Variables relevantes:

```text
SECRET_KEY
DEBUG
ALLOWED_HOSTS
DATABASE_URL
DB_HOST
DB_NAME
DB_USER
DB_PASSWORD
DB_PORT
DB_SSLMODE
CORS_ALLOWED_ORIGINS
CORS_ALLOWED_ORIGIN_REGEXES
CSRF_TRUSTED_ORIGINS
SESSION_COOKIE_SAMESITE
CSRF_COOKIE_SAMESITE
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
PUSHER_APP_ID
PUSHER_KEY
PUSHER_SECRET
PUSHER_CLUSTER
```

## Base de Datos

Prioridad de configuracion:

1. `DATABASE_URL`
2. `DB_HOST` para PostgreSQL
3. SQLite local como fallback

Conexion local desde herramienta externa:

```text
Host: localhost
Port: 5432
Database: nurax_db
Username: nurax_user
Password: nurax_password
```

## Auth y Cookies

En desarrollo, `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` quedan en `False` si `DEBUG=True`.

En produccion:

- `DEBUG=False`
- cookies seguras activas
- `SameSite=None` si el frontend vive en otro dominio
- `CSRF_TRUSTED_ORIGINS` debe incluir el dominio frontend

## Cloudinary

Usado para:

- Avatar de usuario
- Logo de tienda
- Imagen de producto

Si Cloudinary no esta configurado, los endpoints de upload pueden fallar. El resto de la API no depende de imagenes.

## Pusher

Usado por `carts` para emitir `CART_UPDATED` en canales privados:

```text
private-cart-{session_id}
```

Auth:

```text
POST /api/pusher/auth/
```

## Troubleshooting

Ver contenedores:

```bash
docker ps
```

Logs:

```bash
docker logs -f nurax_api
docker logs -f nurax_db
```

Reiniciar limpio sin borrar volumen:

```bash
docker compose down
docker compose up --build
```

Borrar base local Docker:

```bash
docker compose down -v
docker compose up --build
```

Probar salud basica:

```bash
docker exec nurax_api python manage.py check
docker exec nurax_api python manage.py test apps.accounts apps.products apps.inventory apps.expenses apps.sales apps.carts
```
