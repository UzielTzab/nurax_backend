"""
Constantes del sistema centralizadas.
"""

# ─── ESTADOS DE VENTA ───────────────────────────────────────────────────────
SALE_STATUS_COMPLETED = 'completed'
SALE_STATUS_PENDING = 'pending'
SALE_STATUS_CANCELLED = 'cancelled'
SALE_STATUS_CREDIT = 'credit'
SALE_STATUS_LAYAWAY = 'layaway'

# ─── LÍMITES DE STOCK ───────────────────────────────────────────────────────
LOW_STOCK_THRESHOLD = 10
CRITICAL_STOCK_THRESHOLD = 5

# ─── LÍMITES DE PAGINACIÓN ──────────────────────────────────────────────────
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 20

# ─── ROLES DE USUARIO ───────────────────────────────────────────────────────
ROLE_ADMIN = 'admin'
ROLE_CLIENTE = 'cliente'

# ─── TIPOS DE TRANSACCIÓN DE INVENTARIO ─────────────────────────────────────
TRANSACTION_TYPE_IN = 'in'
TRANSACTION_TYPE_OUT = 'out'
TRANSACTION_TYPE_ADJUSTMENT = 'adjustment'
TRANSACTION_TYPE_WASTE = 'waste'

# ─── CATEGORÍAS DE GASTOS ───────────────────────────────────────────────────
EXPENSE_CATEGORY_SERVICIOS = 'servicios'
EXPENSE_CATEGORY_NOMINA = 'nomina'
EXPENSE_CATEGORY_PROVEEDORES = 'proveedores'
EXPENSE_CATEGORY_INVENTARIO = 'inventario'
EXPENSE_CATEGORY_VARIOS = 'varios'

# ─── TIPOS DE MOVIMIENTO DE INVENTARIO ──────────────────────────────────────
MOVEMENT_TYPE_SALE = 'sale'
MOVEMENT_TYPE_RESTOCK = 'restock'
MOVEMENT_TYPE_ADJUST = 'adjust'

# ─── MENSAJES COMUNES ───────────────────────────────────────────────────────
MSG_SUCCESS = "Operación realizada correctamente"
MSG_ERROR = "Error al procesar la solicitud"
MSG_NOT_FOUND = "Recurso no encontrado"
MSG_PERMISSION_DENIED = "Permiso denegado"
