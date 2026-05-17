# Documentacion Backend

Esta carpeta contiene solo la documentacion viva del backend. La fuente de verdad es el codigo actual en `apps/`, `core/`, `utils/`, `docker-compose.yml` y `requirements.txt`.

El nombre oficial de la arquitectura actual es **Arquitectura Final**.

## Lectura Recomendada

1. [Arquitectura Final](./ARQUITECTURA_FINAL.md)
2. [API](./API.md)
3. [Desarrollo](./DESARROLLO.md)
4. [Operacion](./OPERACION.md)
5. [Historial de refactor](./HISTORIAL_REFACTOR.md)

## Reglas de Mantenimiento

- No documentar comportamiento que no exista en el codigo.
- No duplicar listas grandes de endpoints si Swagger ya las expone en `/api/docs/`.
- Cuando cambien modelos, serializers, viewsets o settings, actualizar primero `ARQUITECTURA_FINAL.md` y despues `API.md` si aplica.
- Las guias historicas no deben volver al directorio principal de `docs`.

## Validacion Rapida

```bash
docker exec nurax_api python manage.py test apps.accounts apps.products apps.inventory apps.expenses apps.sales apps.carts
```

Swagger local:

```text
http://localhost:8000/api/docs/
```
