# Flujos de Negocio - Nurax Backend

Diagramas visuales de los procesos principales del sistema.

---

## Flujo 1: Venta Completa (Pago Inmediato)

```
Cliente llega a tienda
        │
        ▼
Vendedor agrega productos al carrito
(ActiveSessionCart)
        │
        ▼
Cliente paga en el acto
        │
        ▼
Crear SALE
├─ transaction_id (generado automático)
├─ status: "completed"
├─ total: suma de items
├─ amount_paid: total
└─ customer_name, customer_phone
        │
        ▼
Crear SALE_ITEMs (uno por producto)
├─ product_id (referencia)
├─ product_name (snapshot)
├─ quantity
└─ unit_price
        │
        ▼
Actualizar PRODUCT stock
(Decrementar por cantidad vendida)
        │
        ▼
Registrar en INVENTORY_MOVEMENT
├─ movement_type: "sale"
├─ quantity: (negativo)
└─ cash_shift_id: turno actual
        │
        ▼
✅ Venta Completada:
- Imprime recibo
- Actualiza dashboard
- Incrementa totales del turno
```

---

## Flujo 2: Venta a Crédito

```
Cliente quiere comprar pero sin dinero completo
        │
        ▼
Crear SALE
├─ status: "credit"
├─ total: monto completo
├─ amount_paid: null o monto inicial
└─ customer_name, customer_phone
        │
        ▼
Crear SALE_ITEMs (como en flujo 1)
        │
        ▼
Actualizar PRODUCT stock
(Décrementar igual que en venta normal)
        │
        ▼
Usuario realiza ABONOS (SALE_PAYMENTs)
┌─────────────────────────────────┐
│ Primer abono                      │
├─ amount: $500 (de los $1000 owed) │
└─ created_at: hoy               │
│                                  │
│ Segundo abono (1 semana después) │
├─ amount: $500 (completa)         │
└─ status sale pasa de "credit"
    a "completed"
└─────────────────────────────────┘
        │
        ▼
✅ Venta Cerrada:
- balance_due = 0
- Historial de abonos disponible
```

---

## Flujo 3: Reabastecimiento (Compra a Proveedor)

```
Gerente verifica stock bajo
        │
        ▼
Contacta Proveedor (SUPPLIER)
        │
        ▼
Recibe mercancía
        │
        ▼
Abrir o usar CASH_SHIFT actual
        │
        ▼
Registrar INVENTORY_MOVEMENT
├─ product: ítem comprado
├─ movement_type: "restock"
├─ quantity: cantidad recibida (ej: 50)
├─ unit_cost: costo unitario (ej: $90)
├─ total_cost: quantity × unit_cost
└─ cash_shift_id: turno actual
        │
        ▼
Actualizar PRODUCT
└─ stock += quantity (aumenta)
        │
        ▼
Registrar EXPENSE (opcional)
├─ amount: total_cost
├─ category: "inventario"
├─ supplier: referencia a proveedor
├─ cash_shift: turno actual
└─ receipt_url: foto de factura
        │
        ▼
✅ Stock Actualizado:
- Producto tiene nuevo stock
- Expense registrado para auditoría
- CashShift refleja egreso
```

---

## Flujo 4: Corte de Caja (Cash Shift)

```
Inicio de turno
        │
        ▼
Vendedor ABRE TURNO (CashShift)
├─ starting_cash: $500 (dinero inicial)
└─ opened_at: TIMESTAMP
        │
        ▼
Durante el turno:
┌──────────────────────────────┐
│ • Ventas completadas         │
│ • Pagos a proveedores        │
│ • Gastos registrados         │
│ • Reabastecimiento           │
│ • Devoluciones               │
└──────────────────────────────┘
        │
        ▼
Fin de turno: CIERRA CASHSHIFT
        │
        ▼
Ingresar dinero real en caja (amount_paid)
        │
        ▼
Sistema CALCULA:
├─ expected_cash = starting_cash
│                + sum(ventas)
│                - sum(gastos)
│                - sum(pagos_proveedores)
│
└─ actual_cash = dinero real contado
        │
        ▼
Calcular DIFERENCIA
└─ difference = actual_cash - expected_cash
        │
        ▼
Resultados:
┌────────────────────────────────────┐
│ difference = 0                     │
│ ✅ Cuadratura perfecta             │
│                                    │
│ difference > 0                     │
│ 💰 Ganancia extra (sobrante)       │
│                                    │
│ difference < 0                     │
│ ⚠️ Faltante (revisar)              │
└────────────────────────────────────┘
        │
        ▼
✅ Turno Cerrado:
- Reporte para auditoría
- Histórico de movimientos
- Fecha/hora de apertura Y cierre
```

---

## Flujo 5: Ajuste de Inventario

```
Realizar CONTEO FÍSICO de productos
        │
        ▼
Sistema muestra: 50 unidades
Realidad: 45 unidades
        │
        ▼
Diferencia = -5 unidades (merma)
        │
        ▼
Registrar INVENTORY_TRANSACTION
├─ transaction_type: "adjustment"
├─ quantity: -5
├─ reason: "Conteo físico - faltantes"
└─ user: quién lo registró
        │
        ▼
Actualizar PRODUCT.stock
└─ stock = 45
        │
        ▼
Opcionalmente registrar EXPENSE
├─ amount: valor de lo perdido
├─ category: "varios" o "inventario"
└─ description: razón de la merma
        │
        ▼
✅ Stock Correcto:
- Sistema = Realidad
- Merma registrada
- Auditoría disponible
```

---

## Flujo 6: Gestión de Categorías y Productos

```
CREAR CATEGORÍA
┌──────────────────────┐
│ Nombre: "Electrónica"│
└──────────────────────┘
        ▼
Guardado en CATEGORY
        │
        │
CREAR PRODUCTO
┌────────────────────────────────┐
│ name: "iPhone 15"              │
│ sku: "IPHONE-15"               │
│ category: Electrónica          │
│ supplier: Apple (proveedor)    │
│ stock: 0                       │
│ price: $999.99                 │
│ image_url: URL en Cloudinary   │
└────────────────────────────────┘
        ▼
Guardado en PRODUCT
        │
        ▼
Estado inicial del producto:
└─ status = "out_of_stock" (stock = 0)
        │
        ▼
Reabastecimiento:
├─ Agregar 50 unidades
└─ stock = 50 → status = "in_stock"
        │
        ▼
Stock va a 12 unidades
└─ status = "low_stock" (≤10)
        │
        ▼
Stock va a 8 unidades
└─ status = "low_stock" (⚠️ alerta)
        │
        ▼
Stock llega a 0
└─ status = "out_of_stock" (no se puede vender)
        │
        ▼
✅ Ciclo de vida completo
```

---

## Flujo 7: Gestión de Gastos

```
REGISTRAR GASTO
┌─────────────────────────────────────┐
│ category: "servicios"               │
│ (opciones: servicios, nómina,       │
│  proveedores, inventario, varios)   │
│                                     │
│ description: "Pago factura internet"│
│ amount: $150.00                     │
│ supplier: ISP (opcional)            │
│ receipt_url: URL de comprobante     │
│ date: automático (hoy)              │
└─────────────────────────────────────┘
        │
        ▼
Gasto se registra en EXPENSE
        │
        ▼
Se vincula automáticamente a CASH_SHIFT
(si hay turno abierto)
        │
        ▼
Afecta el CÁLCULO de CashShift
├─ expected_cash -= amount
└─ Al cerrar turno, se refleja en diferencia
        │
        ▼
️📊 Análisis de Gastos
├─ Por categoría
├─ Por día/mes
├─ Por proveedor
└─ Total vs presupuesto
        │
        ▼
✅ Auditoría Completa:
- Quién registró
- Cuándo
- Comprobante disponible
- Afecta finanzas
```

---

## Flujo 8: Autenticación y Sesión

```
Usuario abre aplicación
        │
        ▼
Ingresa email y password
        │
        ▼
API: POST /api/token/
├─ Valida credenciales
├─ Si ✅ válido:
│   └─ Retorna access_token + refresh_token
│
└─ Si ❌ inválido:
    └─ Retorna error 401
        │
        ▼
Frontend almacena tokens
├─ access: en memoria o sessionStorage
├─ refresh: en cookie httpOnly (seguro)
└─ Duración: access = corto (15 min), refresh = largo (7 días)
        │
        ▼
Todas las peticiones incluyen:
├─ Authorization: Bearer <access_token>
└─ API valida token en cada request
        │
        ▼
Si access_token expira:
├─ Frontend detecta error 401
├─ Usa refresh_token para obtener nuevo access
└─ Reintenta request original
        │
        ▼
Si refresh_token expira:
├─ Usuario debe logout
└─ Volver a autenticarse
        │
        ▼
✅ Sesión Segura:
- Tokens con expiración
- Frontend/Backend sincronizados
- Revocación posible
- Datos aislados por usuario
```

---

## Relaciones entre Entidades

```
┌─────────────────────────────────────────────────────────────┐
│                         USER (Centro)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Propietario de:                                             │
│  ├─ STORE_PROFILE → Configuración tienda                   │
│  ├─ ACTIVE_SESSION_CART → Carrito actual                   │
│  ├─ PRODUCTs → Inventario                                  │
│  ├─ SUPPLIERs → Lista de proveedores                       │
│  ├─ SALEs → Transacciones realizadas                       │
│  ├─ CASH_SHIFTs → Cortes/turnos                            │
│  ├─ EXPENSEs → Gastos registrados                          │
│  └─ [INVENTORY_TRANSACTIONS, MOVEMENTS, PAYMENTS]           │
│                                                              │
│  Vinculaciones:                                              │
│  ├─ PRODUCTs → CATEGORY (no es owner)                      │
│  ├─ PRODUCTs → SUPPLIER (opcional)                         │
│  ├─ SALEs → SALEITEMs (uno a muchos)                       │
│  ├─ SALEs → SALEPAYMENTs (abonos)                          │
│  └─ SALEs → PRODUCTs (via SALEITEM)                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Estados y Transiciones

### **Estados de SALE**

```
                    ┌──────────────┐
                    │   PENDING    │
                    └──────┬───────┘
                           │
                    ┌──────▼────────┐
    ┌──────────────→│    CREDIT     │
    │               └──────┬────────┘
    │                      │
    │          (después de abonos)
    │                      │
    │               ┌──────▼────────┐
    │       ┌──────→│   COMPLETED   │
    │       │       └───────────────┘
    │       │
    │  ┌────┴────────┐
    │  │ LAYAWAY     │  (apartado)
    │  │ (pagos      │
    │  │  parciales) │
    │  └────┬────────┘
    │       │
    └───────┘
    
    Cualquier estado → CANCELLED
```

### **Estados de CASH_SHIFT**

```
start
  │
  ▼
┌──────────────┐
│  OPEN        │  (abierto - con starting_cash)
│ opened_at    │
└──────┬───────┘
       │
 (durante turno: movimientos, gastos)
       │
       ▼
┌──────────────┐
│  CLOSED      │  (cerrado + reconciliado)
│ closed_at    │
│ actual_cash  │
│ difference   │
└──────────────┘
```

---

## Datos que Fluyen por el Sistema

### **En una VENTA**

```
INPUT:
┌────────────────────┐
│ Items en carrito   │
│ • Producto ID      │
│ • Cantidad         │
│ • Precio unitario  │
├────────────────────┤
│ Datos cliente      │
│ • Nombre           │
│ • Teléfono         │
│ • Método pago      │
└────────────────────┘
       │
       ▼
PROCESAMIENTO:
┌────────────────────┐
│ Crear SALE         │
│  ├─ transaction_id │
│  ├─ total (calc)   │
│  └─ status         │
│                    │
│ Crear SALEITEMs    │
│  ├─ product_id     │
│  ├─ quantity       │
│  └─ subtotal (calc)│
│                    │
│ Actualizar stock   │
│  └─ PRODUCT-qty    │
│                    │
│ Registrar movto    │
│  └─ InventoryMove  │
└────────────────────┘
       │
       ▼
OUTPUT:
┌────────────────────┐
│ Recibo de venta    │
│ • Transaction ID   │
│ • Items vendidos   │
│ • Total pagado     │
│ • Fecha/Hora       │
│ • Vendedor         │
└────────────────────┘
```

---

**Última actualización:** Marzo 2026
