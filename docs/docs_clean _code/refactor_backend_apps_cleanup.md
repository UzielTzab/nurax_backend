# Refactorizacion y Limpieza de Apps Backend

**Fecha:** 17 de Mayo de 2026
**Objetivo:** Completar la limpieza iniciada en `products` sobre las demas apps del backend, eliminando rastros V1, validadores muertos, tests obsoletos y compatibilidad legacy innecesaria.

---

## Apps Revisadas

- `accounts`
- `carts`
- `expenses`
- `inventory`
- `sales`

---

## Cambios Principales

### 1. Tests actualizados a ARCHITECTURE_V2

Se reescribieron los tests que todavia usaban modelos y campos antiguos:

- `accounts/tests.py`: se quitaron referencias a `StoreProfile` y `ActiveSessionCart`; ahora valida `User`, `Store`, `StoreMembership`, `Client` y `StoreWithOwnerSerializer`.
- `inventory/tests.py`: se elimino `InventoryTransaction`; ahora cubre `InventoryMovement` con `Product.current_stock`.
- `expenses/tests.py`: se alineo `Expense` a `ExpenseCategory`, `Store` y `CashShift.opened_by`.
- `sales/tests.py`: se sustituyeron campos legacy como `user`, `total`, `stock`, `sku` y estados antiguos por `store`, `total_amount`, `current_stock`, `Sale.Status` y `Sale.SaleType`.

### 2. Managers alineados a modelos actuales

- `inventory/managers.py`: ahora expone `InventoryMovementQuerySet` y `InventoryMovementManager` con filtros por entradas, salidas y tienda.
- `expenses/managers.py`: se conservaron `ExpenseManager` y `CashShiftManager`, limpiando docstrings redundantes y permitiendo filtrar gastos por categoria real.
- `sales/managers.py`: se reemplazaron estados V1 (`completed`, `pending`) por estados V2 (`paid`, `partial`, `cancelled`).
- Los managers de `inventory`, `expenses` y `sales` quedaron conectados a sus modelos correspondientes.

### 3. Serializers y flujo de ventas

En `sales/serializers.py` se limpio `SaleCreateSerializer`:

- Se elimino el calculo duplicado de `amount_tendered` y `change`.
- Se reemplazaron abreviaturas como `qty` por nombres declarativos.
- Se extrajo la creacion de items y movimientos de inventario a metodos privados.
- Se mantuvo el flujo transaccional y la actualizacion de `current_stock`.

### 4. Validadores sin uso

Los validadores personalizados de `accounts`, `inventory`, `expenses` y `sales` no tenian referencias activas. Se dejaron como modulos marcador, igual que en `products`, para evitar importaciones rotas y delegar validacion a modelos y serializers.

### 5. Compatibilidad legacy retirada

En `expenses/views.py` se elimino el endpoint legacy `POST /cash-shifts/open/`. La apertura de turno queda centralizada en el endpoint limpio:

```text
POST /api/v1/expenses/cash-shifts/
```

---

## Validacion

Se ejecuto la suite dentro del contenedor Docker:

```text
docker exec nurax_api python manage.py test apps.accounts apps.inventory apps.expenses apps.sales apps.carts
```

Resultado:

```text
Ran 34 tests in 21.666s
OK
```

---

## Beneficios

1. Las pruebas ya no dependen de modelos V1 inexistentes.
2. La logica de ventas queda mas legible y sin calculos duplicados.
3. Managers y validadores dejan de comunicar conceptos obsoletos.
4. La API queda mas estricta y consistente con el modelo multi-tienda actual.
