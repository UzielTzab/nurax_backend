# Nurax Backend

Backend Django REST Framework de Nurax.

La documentacion activa esta compactada en [`docs/`](./docs/README.md). La arquitectura actual se llama **Arquitectura Final**.

## Inicio Rapido

```bash
docker compose up --build
```

Servicios:

- API: `http://localhost:8000`
- Admin: `http://localhost:8000/admin/`
- Swagger: `http://localhost:8000/api/docs/`
- PostgreSQL: `localhost:5432`

## Comandos Comunes

```bash
docker exec nurax_api python manage.py migrate
docker exec nurax_api python manage.py makemigrations
docker exec nurax_api python manage.py test
docker exec -it nurax_api python manage.py shell
```

Pruebas por apps principales:

```bash
docker exec nurax_api python manage.py test apps.accounts apps.products apps.inventory apps.expenses apps.sales apps.carts
```

## Documentos Clave

- [Arquitectura Final](./docs/ARQUITECTURA_FINAL.md)
- [API](./docs/API.md)
- [Desarrollo](./docs/DESARROLLO.md)
- [Operacion](./docs/OPERACION.md)
- [Historial de refactor](./docs/HISTORIAL_REFACTOR.md)
