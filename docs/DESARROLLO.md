# Desarrollo

## Fuente de Verdad

Antes de actualizar documentacion o crear una feature, revisar el codigo real:

- Modelos: `apps/*/models.py`
- Serializers: `apps/*/serializers.py`
- Viewsets: `apps/*/views.py`
- Rutas: `core/urls.py` y `apps/*/urls.py`
- Configuracion: `core/settings.py`

## Comandos con Docker

```bash
docker compose up --build
docker compose up
docker compose down
```

Tests:

```bash
docker exec nurax_api python manage.py test
docker exec nurax_api python manage.py test apps.accounts apps.products apps.inventory apps.expenses apps.sales apps.carts
```

Migraciones:

```bash
docker exec nurax_api python manage.py makemigrations
docker exec nurax_api python manage.py migrate
docker exec nurax_api python manage.py showmigrations
```

Shell:

```bash
docker exec -it nurax_api python manage.py shell
```

## Convenciones

- Mantener la logica multi-tienda basada en `StoreMembership`.
- Usar `Product.current_stock`; no reintroducir campos antiguos como `stock` o `sku` en `Product`.
- Para cambios de stock, crear `InventoryMovement`.
- Para ventas, usar `Sale`, `SaleItem` y `SalePayment`.
- Para caja, abrir turno con `POST /api/v1/expenses/cash-shifts/`.
- Los validadores personalizados estan vacios si la validacion ya vive en modelos/serializers.
- Evitar comentarios que repitan el nombre del metodo.

## Agregar un Endpoint

1. Crear o actualizar modelo.
2. Crear migracion.
3. Actualizar serializer.
4. Actualizar viewset o APIView.
5. Registrar ruta.
6. Agregar pruebas.
7. Actualizar `docs/API.md` si cambia la superficie publica.

## Agregar un Campo de Modelo

1. Modificar `models.py`.
2. Revisar serializers y admin.
3. Crear migracion.
4. Actualizar tests.
5. Actualizar `docs/ARQUITECTURA_FINAL.md`.

## Pruebas Minimas por Cambio

- Modelo: creacion, representacion y propiedades.
- Serializer: validaciones y campos derivados.
- Viewset/API: permisos, filtros y acciones custom.
- Flujos con stock: verificar `current_stock` y `InventoryMovement`.

## Limpieza de Codigo

Se permite borrar deuda si:

- La ruta no es usada por frontend ni documentacion actual.
- El test demuestra el comportamiento nuevo.
- No queda compatibilidad legacy que esconda contratos rotos.

Si hay duda, preferir una migracion o PR pequeno antes que una limpieza grande.
