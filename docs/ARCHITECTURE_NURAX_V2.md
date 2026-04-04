---
config:
  layout: elk
  theme: redux-color
---
erDiagram
    %% ==========================================
    %% 1. IDENTIDAD Y ACCESO
    %% ==========================================
    STORE {
        uuid id PK
        string name "Ej: Electrónica Nurax"
        string plan "Pro, Básico"
        string tax_id
    }
    USER {
        uuid id PK
        string email
        string password
    }
    STORE_MEMBERSHIP {
        uuid id PK
        uuid store_id FK
        uuid user_id FK
        string role "Owner, Manager, Cashier"
    }

    %% ==========================================
    %% 2. CATÁLOGO Y PROVEEDORES
    %% ==========================================
    CATEGORY {
        uuid id PK
        uuid store_id FK
        string name "Ej: Cables, Audio"
    }
    SUPPLIER {
        uuid id PK
        uuid store_id FK
        string name
        string contact_info
    }
    PRODUCT {
        uuid id PK
        uuid store_id FK
        uuid category_id FK
        uuid supplier_id FK
        string name
        decimal base_cost "Costo real para el dueño"
        decimal sale_price "Precio al público"
        int current_stock
    }
    PRODUCT_PACKAGING {
        uuid id PK
        uuid product_id FK
        string name "Ej: Caja con 50"
        int quantity_per_unit
    }
    PRODUCT_CODE {
        uuid id PK
        uuid product_id FK
        string code "El valor del QR o Barras"
        string type "EAN13, QR, UPC, SHELF_LABEL"
    }

    %% ==========================================
    %% 3. CAJA Y FLUJO
    %% ==========================================
    CASH_SHIFT {
        uuid id PK
        uuid store_id FK
        uuid opened_by FK "Usuario que abrió la caja"
        datetime opened_at
        datetime closed_at "NULL si el turno sigue abierto"
        decimal starting_cash "Fondo de caja"
    }
    CASH_MOVEMENT {
        uuid id PK
        uuid shift_id FK
        string movement_type "IN (Entrada) / OUT (Salida)"
        decimal amount
        string reason "Ej: Venta #10, Pago internet"
        datetime created_at
    }

    %% ==========================================
    %% 4. CLIENTES
    %% ==========================================
    CUSTOMER {
        uuid id PK
        string name
        decimal credit_limit
    }

    %% ==========================================
    %% 5. VENTAS Y CRÉDITOS
    %% ==========================================
    SALE {
        uuid id PK
        uuid store_id FK
        uuid cash_shift_id FK "A qué turno entró este dinero"
        uuid customer_id FK "Opcional (Null si es venta rápida)"
        string status "PAID, PARTIAL, CANCELLED"
        decimal total_amount "Total a cobrar"
        decimal amount_paid "Suma de abonos + pago inicial"
        datetime created_at
    }
    SALE_ITEM {
        uuid id PK
        uuid sale_id FK
        uuid product_id FK
        int quantity
        decimal unit_price "Snapshot: Precio al que se vendió"
        decimal unit_cost "Snapshot: Costo al momento de venta"
    }
    SALE_PAYMENT {
        uuid id PK
        uuid sale_id FK
        uuid cash_shift_id FK
        decimal amount
        datetime created_at
    }

    %% ==========================================
    %% 6. KÁRDEX / AUDITORÍA
    %% ==========================================
    INVENTORY_MOVEMENT {
        uuid id PK
        uuid product_id FK
        uuid user_id FK "Quién hizo el movimiento"
        string type "SALE, PURCHASE, ADJUSTMENT, RETURN"
        int quantity "Ej: -2 (Venta), +50 (Compra)"
        int stock_before "Stock antes del movimiento"
        int stock_after "Stock exacto resultante"
        datetime created_at
    }

    %% ==========================================
    %% 7. COMPRAS A PROVEEDORES
    %% ==========================================
    PURCHASE_ORDER {
        uuid id PK
        uuid store_id FK
        uuid supplier_id FK
        string status "PENDING, RECEIVED, CANCELLED"
        decimal total_cost
        datetime created_at
    }
    PURCHASE_ORDER_ITEM {
        uuid id PK
        uuid purchase_order_id FK
        uuid product_id FK
        int quantity
        decimal unit_cost
    }

    %% ==========================================
    %% 8. GASTOS OPERATIVOS
    %% ==========================================
    EXPENSE_CATEGORY {
        uuid id PK
        uuid store_id FK
        string name "Ej: Servicios, Nómina, Compras"
    }
    EXPENSE {
        uuid id PK
        uuid store_id FK
        uuid category_id FK
        uuid cash_shift_id FK "Opcional: Nulo si se pagó por banco"
        uuid purchase_order_id FK "Opcional: Si es gasto de mercancía"
        decimal amount
        string description
        string payment_method "CASH, TRANSFER, CARD"
        datetime created_at
    }

    %% ==========================================
    %% 9. CARRITO EN TIEMPO REAL (WEBSOCKETS)
    %% ==========================================
    ACTIVE_CART {
        uuid id PK
        uuid store_id FK
        uuid user_id FK "Quién lo está llenando"
        string session_id "Para identificar el canal de Pusher"
        decimal total_temp
        datetime updated_at
    }
    CART_ITEM {
        uuid id PK
        uuid cart_id FK
        uuid product_id FK
        int quantity
        decimal unit_price_at_time
    }

    %% ==========================================
    %% RELACIONES COMPLETAS
    %% ==========================================
    
    %% Identidad
    STORE ||--o{ STORE_MEMBERSHIP : "tiene"
    USER ||--o{ STORE_MEMBERSHIP : "pertenece a"
    
    %% Catálogo y Escáner
    STORE ||--o{ CATEGORY : "organiza"
    STORE ||--o{ SUPPLIER : "tiene registrados"
    STORE ||--o{ PRODUCT : "vende"
    CATEGORY ||--o{ PRODUCT : "clasifica"
    SUPPLIER ||--o{ PRODUCT : "provee"
    PRODUCT ||--o{ PRODUCT_PACKAGING : "se agrupa en"
    PRODUCT ||--o{ PRODUCT_CODE : "se escanea con"
    
    %% Caja
    STORE ||--o{ CASH_SHIFT : "registra"
    USER ||--o{ CASH_SHIFT : "opera"
    CASH_SHIFT ||--o{ CASH_MOVEMENT : "contiene"
    
    %% Carrito WebSockets
    STORE ||--o{ ACTIVE_CART : "gestiona"
    USER ||--o{ ACTIVE_CART : "opera"
    ACTIVE_CART ||--o{ CART_ITEM : "contiene"
    PRODUCT ||--o{ CART_ITEM : "se agrega a"
    ACTIVE_CART |o--o| SALE : "se convierte en"

    %% Ventas y Clientes
    STORE ||--o{ SALE : "realiza"
    CASH_SHIFT ||--o{ SALE : "ingresa dinero a"
    CUSTOMER ||--o{ SALE : "tiene"
    SALE ||--o{ SALE_ITEM : "contiene"
    PRODUCT ||--o{ SALE_ITEM : "se vende como"
    SALE ||--o{ SALE_PAYMENT : "recibe"
    CASH_SHIFT ||--o{ SALE_PAYMENT : "procesa"
    
    %% Kárdex
    PRODUCT ||--o{ INVENTORY_MOVEMENT : "tiene historial en"
    USER ||--o{ INVENTORY_MOVEMENT : "registra"

    %% Compras a Proveedores
    STORE ||--o{ PURCHASE_ORDER : "emite"
    SUPPLIER ||--o{ PURCHASE_ORDER : "recibe"
    PURCHASE_ORDER ||--o{ PURCHASE_ORDER_ITEM : "contiene"
    PRODUCT ||--o{ PURCHASE_ORDER_ITEM : "abastece"

    %% Gastos
    STORE ||--o{ EXPENSE_CATEGORY : "define"
    STORE ||--o{ EXPENSE : "registra"
    EXPENSE_CATEGORY ||--o{ EXPENSE : "clasifica"
    CASH_SHIFT ||--o{ EXPENSE : "paga en efectivo"
    PURCHASE_ORDER ||--o{ EXPENSE : "genera"