# Historial de Refactor

Este documento resume limpiezas relevantes. No reemplaza a `ARQUITECTURA_FINAL.md`; solo deja contexto para entender por que se removieron piezas antiguas.

## Products

Se limpio la app `products` para alinearla con la Arquitectura Final:

- `Product` usa `current_stock`, `base_cost` y `sale_price`.
- Las consultas de stock usan `current_stock`.
- Se agrego soporte para `ProductVariation`.
- Se retiro normalizacion de payloads antiguos.
- Los tests se reescribieron con `Store`.
- Validadores muertos quedaron delegados a modelo/serializer.

## Apps Backend Restantes

Se revisaron `accounts`, `inventory`, `expenses`, `sales` y `carts`.

Cambios principales:

- Tests reescritos contra modelos reales.
- Eliminadas referencias a modelos y campos antiguos.
- Managers conectados a modelos actuales.
- Validadores sin uso reducidos a modulos marcador.
- `SaleCreateSerializer` simplificado para evitar calculos duplicados.
- Retirado `POST /cash-shifts/open/`; la apertura de turno usa `POST /cash-shifts/`.

Validacion:

```text
docker exec nurax_api python manage.py test apps.accounts apps.inventory apps.expenses apps.sales apps.carts

Ran 34 tests in 21.666s
OK
```

## Criterio de Limpieza

- El codigo real manda sobre documentos historicos.
- No conservar endpoints de compatibilidad si el frontend ya usa el contrato limpio.
- No mantener tests que fuerzan modelos inexistentes.
- No agregar validadores si Django/DRF ya validan ese campo.
