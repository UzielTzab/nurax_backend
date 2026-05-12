# Refactorización y Limpieza de la App `Products`

**Fecha:** 12 de Mayo de 2026
**Objetivo:** Limpieza de código (Clean Code), refactorización orientada a la arquitectura V2, eliminación de deuda técnica y mejora en la legibilidad.

---

## Resumen de Cambios Generales

Se realizó una revisión profunda de la aplicación `products` para eliminar rastros de código antiguo (Legacy), corregir el uso de variables abreviadas y alinear todos los componentes al modelo de datos actual (`ARCHITECTURE_V2`), el cual se basa en tiendas (`store`), gestión de stock con `current_stock` y soporte para variaciones de producto (`ProductVariation`).

---

## Archivos Modificados

### 1. `managers.py`
- **Refactorización de V1 a V2:** Se modificaron los QuerySets personalizados (`in_stock`, `low_stock`, `out_of_stock`) para evaluar la disponibilidad usando la columna correcta `current_stock` en lugar de la obsoleta `stock`.
- **Optimización de Consultas:** Se corrigió el método `with_related` para hacer `select_related('store')` en lugar de buscar un campo `user` inexistente.
- **Limpieza de Código:** Se eliminaron docstrings redundantes o que describían acciones obvias dictadas por el mismo nombre del método.

### 2. `serializers.py`
- **Integración de Nuevos Modelos:** Se añadió el `ProductVariationSerializer` y se incluyó como un campo anidado de solo lectura (`variations`) dentro del `ProductSerializer`.
- **Claridad de Nomenclatura:** Se renombraron parámetros en los métodos de validación para evitar abreviaturas y dar contexto (ej. `value` pasó a ser `base_cost_value` o `sale_price_value`).
- **Limpieza de Código:** Se eliminaron comentarios de guía obsoletos, manteniendo únicamente los necesarios para explicar la lógica de Cloudinary.

### 3. `views.py`
- **Eliminación de Deuda Técnica:** Se eliminó por completo la función parche `_normalize_payload`. Anteriormente, esta función se utilizaba para mapear campos antiguos enviados por el frontend (como `stock` a `current_stock` e ignorando `sku`). Ahora, en concordancia con Clean Code, el backend espera el formato estricto y limpio.
- **Simplificación:** Los métodos `create` y `update` fueron simplificados al quitar las llamadas a la función de normalización, utilizando directamente `request.data.copy()`.
- **Nuevos Endpoints:** Se implementó `ProductVariationViewSet` para permitir operaciones CRUD sobre las variaciones de los productos.
- **Formato:** Se retiraron saltos de línea innecesarios y comentarios redundantes en las clases.

### 4. `urls.py` & `admin.py`
- **Enrutamiento:** Se registró el enrutador para las variaciones (`router.register('variations', ProductVariationViewSet, basename='variation')`) en `urls.py`.
- **Panel de Administración:** Se agregó `ProductVariationAdmin` en `admin.py` para poder gestionar las variaciones directamente desde el panel de Django.
- **Limpieza de Cabeceras:** Se limpiaron las importaciones y docstrings en ambos archivos.

### 5. `tests.py`
- **Actualización a V2:** Las pruebas fueron reescritas en su totalidad para soportar el nuevo esquema. Las creaciones de instancias de prueba (mocks) ahora instancian un objeto `Store` (en lugar de `User`) y asignan `current_stock`, `base_cost` y `sale_price`.
- **Validación de Nuevos Modelos:** Se añadieron aserciones (tests) para validar el comportamiento y la representación en cadena (`__str__`) de `ProductCode` y `ProductVariation`.

### 6. `validators.py`
- **Eliminación de Código Muerto:** Las funciones `validate_sku_format`, `validate_stock_not_negative` y `validate_positive_decimal` se eliminaron, ya que la validación de estos atributos ya es manejada intrínsecamente por los tipos de campos en Django (`MinValueValidator`, `PositiveIntegerField`, etc.).
- El archivo se dejó vacío (solo con la cabecera) para evitar fallos de importaciones, marcando explícitamente que la lógica fue delegada a los modelos.

---

## Beneficios Obtenidos

1. **Alineación con la Arquitectura:** El backend y el frontend ahora hablan exactamente el mismo idioma sin necesidad de parches intermedios.
2. **Mejor Cobertura y Fiabilidad:** Las pruebas unitarias reflejan el comportamiento real del sistema.
3. **Mantenibilidad:** La eliminación de comentarios inútiles y nombres de variables más declarativos hacen que leer la aplicación sea más fluido para nuevos desarrolladores.
