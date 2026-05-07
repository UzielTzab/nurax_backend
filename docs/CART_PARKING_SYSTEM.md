# Sistema de Carrito con Aparcamiento (Parking)
**Versión:** 1.0  
**Última actualización:** Mayo 7, 2026  
**Estado:** ✅ Completado e Implementado

---

## 📋 Tabla de Contenidos
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura General](#arquitectura-general)
3. [Base de Datos](#base-de-datos)
4. [Backend - Endpoints](#backend---endpoints)
5. [Frontend - SalesModal.vue](#frontend---salesmodalvue)
6. [Flujos de Uso](#flujos-de-uso)
7. [Archivos Modificados](#archivos-modificados)
8. [Testing](#testing)
9. [Notas Técnicas Importantes](#notas-técnicas-importantes)

---

## Resumen Ejecutivo

Se implementó un **sistema completo de carrito compartido con capacidad de aparcamiento** que permite:

- ✅ **Sincronización en tiempo real** entre múltiples dispositivos del mismo usuario mediante Pusher
- ✅ **Persistencia completa en BD** - El carrito es la fuente única de verdad en el backend
- ✅ **Aparcamiento (Parking)** - Pausar una venta y cambiar a otra sin perder datos
- ✅ **Restauración** - Recuperar carritos aparcados y continuar donde se dejó
- ✅ **Sincronización optimista** en frontend para mejor UX
- ✅ **Validación de seguridad** - Solo usuarios autenticados pueden acceder a sus carritos

### Flujo Principal

```
Usuario agrega producto → Frontend (local) → POST /sync-cart/ → Backend (BD)
                                                 ↓
                                         Backend emite Pusher CART_UPDATED
                                                 ↓
                                    Otros dispositivos reciben evento
```

---

## Arquitectura General

### Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUARIO (Cajero)                             │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────┐      ┌──────▼──────┐
         │ Device 1    │      │ Device 2    │
         │ (Tablet)    │      │ (Tablet)    │
         │ SalesModal  │      │ SalesModal  │
         └──────┬──────┘      └──────┬──────┘
                │                     │
                └──────────┬──────────┘
                           │
                  ┌────────▼────────┐
                  │  Pusher Cloud   │
                  │  (Canal privado)│
                  └────────┬────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────────────────────────┐
         │     Django Backend (Carts)      │
         │                                 │
         │  • Modelos (ActiveCart,Items)   │
         │  • Endpoints REST               │
         │  • Broadcasting                 │
         │  • Lógica de negocio            │
         │                                 │
         └──────┬───────────────────────────┘
                │
         ┌──────▼──────────┐
         │  Base de Datos  │
         │  (PostgreSQL)   │
         └─────────────────┘
```

### Componentes Clave

| Componente | Ubicación | Responsabilidad |
|-----------|-----------|-----------------|
| `ActiveCart` | Backend | Modelo de BD para carrito activo/aparcado |
| `CartItem` | Backend | Modelo de BD para items del carrito |
| `CartViewSet` | Backend | Endpoints REST (CRUD + park/restore) |
| `SalesModal.vue` | Frontend | Modal de POS con UI de carrito |
| `Pusher` | Externo | Broadcasting en tiempo real |

---

## Base de Datos

### Modelo `ActiveCart`

```python
class ActiveCart(models.Model):
    id = UUIDField(primary_key=True, default=uuid4)
    store = ForeignKey('accounts.Store', on_delete=models.CASCADE)
    user = ForeignKey('accounts.User', on_delete=models.CASCADE)
    
    # Session para Pusher
    session_id = CharField(max_length=100, unique=True)
    
    # Total temporal
    total_temp = DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Control de aparcamiento
    is_parked = BooleanField(default=False)      # 🆕
    parked_at = DateTimeField(null=True, blank=True)  # 🆕
    
    # Auditoría
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        # Índices para búsquedas rápidas
        indexes = [
            models.Index(fields=['store']),
            models.Index(fields=['user']),
            models.Index(fields=['session_id']),
            models.Index(fields=['is_parked', 'user']),  # 🆕 Para filtrar aparcados
        ]
        verbose_name_plural = 'Active Carts'
    
    def __str__(self):
        status = "Aparcado" if self.is_parked else "Activo"
        return f"Cart {self.id} ({status}) - {self.user}"
```

### Modelo `CartItem`

```python
class CartItem(models.Model):
    id = UUIDField(primary_key=True, default=uuid4)
    cart = ForeignKey('ActiveCart', on_delete=models.CASCADE, related_name='items')
    product = ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = IntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price_at_time = DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
```

### Migración Aplicada

**Archivo:** `nurax_backend/apps/carts/migrations/0002_add_parked_fields.py`

- ✅ Añade campo `is_parked` (BooleanField, default=False)
- ✅ Añade campo `parked_at` (DateTimeField, null=True)
- ✅ Crea índice compuesto en `(is_parked, user)`

**Estado:** Ya migrado y en producción.

---

## Backend - Endpoints

### 1️⃣ GET `/api/v1/carts/carts/my-cart/`

**Propósito:** Obtener el carrito ACTIVO (no aparcado) del usuario autenticado.

**Headers necesarios:**
```
Authorization: Bearer <token_jwt>  (o Cookie con access_token)
```

**Respuesta (200):**
```json
{
  "success": true,
  "data": {
    "cart": [
      {
        "id": "item-uuid-1",
        "product": "product-id",
        "product_name": "Producto A",
        "quantity": 2,
        "unit_price_at_time": "15.50",
        "subtotal": "31.00"
      }
    ],
    "session_id": "device_userid_abc123",
    "active_cart_id": "cart-uuid",
    "total": "31.00"
  }
}
```

**Lógica Interna:**
```python
def get_user_active_cart(user, store=None):
    # Obtener SOLO carritos activos (no aparcados)
    cart = ActiveCart.objects.filter(
        user=user,
        is_parked=False
    ).first()
    
    if not cart:
        return None
    
    return {
        'id': cart.id,
        'session_id': cart.session_id,
        'items': cart.items.all(),
        'total': cart.total_temp
    }
```

**Casos especiales:**
- Si NO existe carrito activo → Retorna `cart: []` vacío pero con estructura completa
- Si usuario tiene múltiples carritos activos → Retorna el más reciente (primera consulta)

---

### 2️⃣ POST `/api/v1/carts/carts/sync-cart/`

**Propósito:** Sincronizar items del carrito local con el servidor (upsert total).

**Request:**
```json
{
  "device_id": "device_1234567890_abc123",
  "cart": [
    {
      "id": "product-uuid",
      "quantity": 2,
      "sale_price": "15.50",
      "store": "store-uuid"
    },
    {
      "id": "product-uuid-2",
      "quantity": 1,
      "sale_price": "25.00",
      "store": "store-uuid"
    }
  ]
}
```

**Respuesta (200):**
```json
{
  "success": true,
  "data": {
    "cart": [
      {
        "id": "item-uuid-1",
        "product": "product-id",
        "product_name": "Producto A",
        "quantity": 2,
        "unit_price_at_time": "15.50",
        "subtotal": "31.00"
      },
      {
        "id": "item-uuid-2",
        "product": "product-id-2",
        "product_name": "Producto B",
        "quantity": 1,
        "unit_price_at_time": "25.00",
        "subtotal": "25.00"
      }
    ],
    "session_id": "device_userid_abc123",
    "active_cart_id": "cart-uuid",
    "total": "56.00"
  }
}
```

**Lógica Interna:**
```python
def sync_cart(user, store, device_id, items_payload):
    # 1. Obtener o crear carrito activo
    cart, created = ActiveCart.objects.get_or_create(
        user=user,
        store=store,
        is_parked=False,
        defaults={'session_id': device_id}
    )
    
    # 2. Upsert items (usar update_or_create)
    for item_data in items_payload:
        product = Product.objects.get(id=item_data['id'])
        CartItem.objects.update_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': item_data['quantity'],
                'unit_price_at_time': item_data['sale_price']
            }
        )
    
    # 3. Eliminar items NO presentes en payload
    existing_product_ids = {item['id'] for item in items_payload}
    CartItem.objects.filter(
        cart=cart
    ).exclude(
        product_id__in=existing_product_ids
    ).delete()
    
    # 4. Recalcular total
    cart.total_temp = cart.items.aggregate(
        total=Sum(F('quantity') * F('unit_price_at_time'))
    )['total'] or 0
    cart.save()
    
    # 5. BROADCAST evento Pusher
    _broadcast_cart_updated(cart.session_id, cart.id, device_id)
    
    return cart
```

**⚡ Comportamiento Importante:**
- ✅ **Upsert:** Actualiza items existentes, agrega nuevos
- ✅ **Elimina items NO en payload:** Si frontend envía `[A, B]` pero antes había `[A, B, C]`, elimina C
- ✅ **Emite Pusher:** Notifica a otros dispositivos del mismo usuario
- ✅ **Recalcula total:** Siempre actualiza el total_temp

---

### 3️⃣ POST `/api/v1/carts/carts/{id}/park/`

**Propósito:** Aparcar (guardar) el carrito actual y crear uno nuevo vacío.

**Request:**
```
POST /api/v1/carts/carts/550e8400-e29b-41d4-a716-446655440000/park/
Content-Type: application/json
Authorization: Bearer <token>
Body: {} (vacío)
```

**Respuesta (200):**
```json
{
  "success": true,
  "message": "Carrito aparcado exitosamente",
  "data": {
    "parked_cart": {
      "id": "parked-cart-uuid",
      "session_id": "old_device_session",
      "total": "150.50",
      "items_count": 3,
      "parked_at": "2026-05-07T10:30:00Z"
    },
    "new_active_cart": {
      "id": "fresh-cart-uuid",
      "session_id": "fresh-device-session-uuid",
      "total": "0.00",
      "items": []
    }
  }
}
```

**Lógica Interna:**
```python
def park_cart(cart_id, user):
    cart = ActiveCart.objects.get(id=cart_id, user=user)
    
    # Validación: No puede estar ya aparcado
    if cart.is_parked:
        raise ValidationError("Carrito ya está aparcado")
    
    # 1. Marcar como aparcado
    cart.is_parked = True
    cart.parked_at = timezone.now()
    cart.save()
    
    # 2. Crear nuevo carrito activo
    new_cart = ActiveCart.objects.create(
        user=user,
        store=cart.store,
        session_id=str(uuid4()),
        is_parked=False,
        total_temp=0
    )
    
    # 3. BROADCAST evento (opcional, para UI en tiempo real)
    _broadcast_cart_updated(cart.session_id, cart.id)
    
    return {
        'parked_cart': {
            'id': cart.id,
            'session_id': cart.session_id,
            'total': cart.total_temp,
            'items_count': cart.items.count(),
            'parked_at': cart.parked_at
        },
        'new_active_cart': {
            'id': new_cart.id,
            'session_id': new_cart.session_id,
            'total': 0,
            'items': []
        }
    }
```

**⚠️ Comportamiento:**
- ✅ Marca carrito como `is_parked=True`
- ✅ Registra timestamp en `parked_at`
- ✅ Crea nuevo carrito VACÍO e activo
- ✅ Retorna ambos para que frontend actualice su estado
- ❌ NO elimina el carrito aparcado (se mantiene en BD)

---

### 4️⃣ GET `/api/v1/carts/carts/parked/`

**Propósito:** Listar todos los carritos aparcados del usuario autenticado.

**Respuesta (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "parked-cart-uuid-1",
      "session_id": "old_session_1",
      "store_name": "Tienda Principal",
      "total": "125.50",
      "items_count": 3,
      "parked_at": "2026-05-07T10:15:00Z"
    },
    {
      "id": "parked-cart-uuid-2",
      "session_id": "old_session_2",
      "store_name": "Tienda Principal",
      "total": "89.99",
      "items_count": 2,
      "parked_at": "2026-05-07T09:45:00Z"
    }
  ]
}
```

**Lógica Interna:**
```python
def list_parked_carts(user):
    carts = ActiveCart.objects.filter(
        user=user,
        is_parked=True
    ).select_related('store').prefetch_related('items')
    
    result = []
    for cart in carts:
        result.append({
            'id': cart.id,
            'session_id': cart.session_id,
            'store_name': cart.store.name,
            'total': cart.total_temp,
            'items_count': cart.items.count(),
            'parked_at': cart.parked_at
        })
    
    return result
```

**📊 Casos de uso:**
- Mostrar contador en UI: `len(parked_carts)`
- Listar en modal para usuario seleccione cuál restaurar
- Ordenar por `parked_at` DESC (más recientes primero)

---

### 5️⃣ POST `/api/v1/carts/carts/{id}/restore/`

**Propósito:** Restaurar un carrito aparcado como carrito activo.

**Request:**
```
POST /api/v1/carts/carts/parked-cart-uuid/restore/
Authorization: Bearer <token>
Body: {} (vacío)
```

**Respuesta (200):**
```json
{
  "success": true,
  "message": "Carrito restaurado exitosamente",
  "data": {
    "cart": [
      {
        "id": "item-uuid-1",
        "product": "product-id",
        "product_name": "Producto A",
        "quantity": 2,
        "unit_price_at_time": "15.50",
        "subtotal": "31.00"
      }
    ],
    "session_id": "new-fresh-session-uuid",
    "active_cart_id": "restored-cart-uuid",
    "total": "31.00"
  }
}
```

**Lógica Interna:**
```python
def restore_parked_cart(cart_id, user):
    parked_cart = ActiveCart.objects.get(id=cart_id, user=user)
    
    # Validación: Debe estar aparcado
    if not parked_cart.is_parked:
        raise ValidationError("Carrito no está aparcado")
    
    # 1. Buscar y eliminar carrito activo anterior (si existe)
    old_active = ActiveCart.objects.filter(
        user=user,
        store=parked_cart.store,
        is_parked=False
    ).first()
    if old_active:
        old_active.delete()
    
    # 2. Restaurar carrito
    parked_cart.is_parked = False
    parked_cart.parked_at = None
    parked_cart.session_id = str(uuid4())  # Generar nuevo session_id
    parked_cart.save()
    
    # 3. BROADCAST evento
    _broadcast_cart_updated(parked_cart.session_id, parked_cart.id)
    
    return {
        'id': parked_cart.id,
        'session_id': parked_cart.session_id,
        'items': parked_cart.items.all(),
        'total': parked_cart.total_temp
    }
```

**⚠️ Comportamiento:**
- ✅ Marca como `is_parked=False`
- ✅ Limpia `parked_at`
- ✅ Genera **nuevo session_id** (es importante para Pusher)
- ✅ **Elimina carrito activo anterior** si existe (no puede haber 2 activos)
- ✅ Retorna items completos para que frontend los muestre

---

### 6️⃣ POST `/api/pusher/auth/`

**Propósito:** Autenticar subscripción a canal privado de Pusher.

**Request:**
```json
{
  "socket_id": "12345.67890",
  "channel_name": "private-cart-device_userid_abc123"
}
```

**Respuesta (200):**
```json
{
  "auth": "pusher_key:hash_signature",
  "channel_data": "{\"user_id\":\"user-uuid\"}"
}
```

**Lógica Interna:**
```python
def pusher_auth(request, channel_name, socket_id):
    user = request.user
    
    # Validación: Canal debe ser del usuario
    if f"private-cart-{user.id}" not in channel_name:
        return Response({'error': 'Unauthorized'}, status=403)
    
    # Delegar a librería Pusher
    pusher_client = get_pusher_client()
    auth_response = pusher_client.authenticate(
        channel=channel_name,
        socket_id=socket_id
    )
    
    return Response(auth_response)
```

**🔒 Seguridad:**
- ✅ Requiere autenticación (JWT)
- ✅ Valida que canal pertenezca al usuario
- ✅ Usa firma HMAC para evitar suplantación

---

### Helper: Broadcasting Pusher

**Función utilitaria:**
```python
def _broadcast_cart_updated(session_id, active_cart_id, device_id=None):
    """Emite evento CART_UPDATED a todos los clientes suscritos"""
    pusher_client = get_pusher_client()
    channel = f"private-cart-{session_id}"
    
    payload = {
        'action': 'CART_UPDATED',
        'active_cart_id': str(active_cart_id),
        'timestamp': timezone.now().isoformat()
    }
    
    if device_id:
        payload['device_id'] = device_id  # Ayuda al cliente a ignorar si es local
    
    try:
        pusher_client.trigger(channel, 'CART_UPDATED', payload)
    except Exception as e:
        logger.error(f"Pusher broadcast failed: {e}")
```

**Dónde se dispara:**
- `sync_cart()` → Después de upsert de items
- `park_cart()` → Después de aparcar
- `restore_parked_cart()` → Después de restaurar

---

## Frontend - SalesModal.vue

### Estado Local (Refs)

```typescript
// Carrito
const cart = ref<CartItem[]>([]);                    // Items visibles en UI
const cartSessionId = ref('');                       // Session ID para Pusher
const activeCartId = ref('');                        // UUID del carrito en BD
const cartTotal = ref(0);                            // Total calculado

// Aparcados
const parkedCarts = ref<ParkedCart[]>([]);          // Lista de carritos aparcados
const parkedCartsCount = ref(0);                     // Contador visual
const showParkedCartsModal = ref(false);             // Modal visible/oculto

// UI
const localDeviceId = `device_${userId}_${randomId}`;  // ID único del dispositivo
const isLoadingCart = ref(false);
const syncInProgress = ref(false);

// Pusher
let cartChannel: any = null;                         // Subscripción actual
```

### Ciclo de Vida - `onMounted`

```typescript
onMounted(async () => {
  try {
    // 1. Cargar datos iniciales
    await loadInventory();          // Productos disponibles
    await loadShifts();             // Turnos del usuario
    
    // 2. Cargar carrito activo y suscribirse a Pusher
    await loadActiveCart();         // GET /my-cart/
    
    // 3. Cargar lista de aparcados (solo contador)
    await loadParkedCartsCount();   // GET /parked/ (para contador)
    
    // 4. Inicializar Pusher
    initializePusher();
    
  } catch (error) {
    console.error('Error en onMounted:', error);
    toast.error('Error al cargar el carrito');
  }
});
```

### Función: `loadActiveCart()`

```typescript
async function loadActiveCart() {
  try {
    isLoadingCart.value = true;
    
    const response = await fetch('/api/v1/carts/carts/my-cart/', {
      headers: authHeaders,
    });
    
    const { success, data } = await response.json();
    
    if (success && data) {
      // Llenar datos locales
      cart.value = data.cart || [];
      cartSessionId.value = data.session_id;
      activeCartId.value = data.active_cart_id;
      cartTotal.value = data.total;
      
      // Suscribirse a cambios en tiempo real
      subscribeToCartChannel(cartSessionId.value);
    }
  } catch (error) {
    console.error('Error loading cart:', error);
    cart.value = [];
  } finally {
    isLoadingCart.value = false;
  }
}
```

### Función: `syncCartToBackend()`

```typescript
async function syncCartToBackend() {
  if (syncInProgress.value) return;  // Evitar múltiples requests
  
  try {
    syncInProgress.value = true;
    
    const payload = {
      device_id: localDeviceId,
      cart: cart.value.map(item => ({
        id: item.product_id,
        quantity: item.quantity,
        sale_price: item.unit_price_at_time,
        store: currentUser.store_profile.id
      }))
    };
    
    const response = await fetch('/api/v1/carts/carts/sync-cart/', {
      method: 'POST',
      headers: { ...authHeaders, 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    
    const { success, data } = await response.json();
    
    if (success) {
      // Actualizar session_id e activeCartId del servidor
      cartSessionId.value = data.session_id;
      activeCartId.value = data.active_cart_id;
      cartTotal.value = data.total;
      
      // Re-suscribirse por si cambió session_id
      subscribeToCartChannel(cartSessionId.value);
    }
  } catch (error) {
    console.error('Sync error:', error);
    toast.error('Error al sincronizar carrito');
  } finally {
    syncInProgress.value = false;
  }
}
```

### Flujo: Agregar Producto

```
Usuario busca/escanea producto en Inventario
         ↓
Click en "+Add"
         ↓
addToCart(product)
  ├─ Valida stock disponible
  ├─ Agrega a cart.value (optimista)
  ├─ Toast "Producto agregado"
  └─ Dispara syncCartToBackend()
         ↓
syncCartToBackend()
  ├─ POST /sync-cart/ con payload
  ├─ Backend upserta en BD
  ├─ Backend emite Pusher CART_UPDATED
  ├─ Frontend recibe evento (ignora si device_id === local)
  └─ Carrito visible actualizado
```

### Flujo: Aparcar Carrito

```
Usuario cliquea botón "📌 Aparcar"
         ↓
parkCart()
  ├─ Validación: ¿hay items?
  │   ├─ NO → Toast error
  │   └─ SÍ → continuar
  ├─ Validación: ¿activeCartId existe?
  │   ├─ NO → Fuerza syncCartToBackend()
  │   └─ SÍ → continuar
  ├─ POST /carts/{activeCartId}/park/
  ├─ Backend crea nuevo carrito
  ├─ Frontend recibe new_active_cart
  ├─ Frontend vacía cart.value = []
  ├─ Frontend cambia session_id
  ├─ Frontend suscribe a nuevo canal
  ├─ Frontend recarga parkedCartsCount
  └─ Toast "Carrito aparcado"
```

### Función: `parkCart()`

```typescript
async function parkCart() {
  try {
    // Validar que hay items
    if (!cart.value.length) {
      toast.warning('No hay productos en el carrito');
      return;
    }
    
    // Validar que activeCartId existe
    if (!activeCartId.value) {
      await syncCartToBackend();  // Fuerza sync para obtener ID
    }
    
    // Enviar request al backend
    const response = await fetch(
      `/api/v1/carts/carts/${activeCartId.value}/park/`,
      {
        method: 'POST',
        headers: authHeaders
      }
    );
    
    const { success, data } = await response.json();
    
    if (success) {
      // Actualizar estado local
      cart.value = [];  // Vaciar UI
      activeCartId.value = data.new_active_cart.id;
      cartSessionId.value = data.new_active_cart.session_id;
      cartTotal.value = 0;
      
      // Suscribirse al nuevo canal
      subscribeToCartChannel(cartSessionId.value);
      
      // Recargar lista de aparcados
      await loadParkedCartsCount();
      
      toast.success('Carrito aparcado exitosamente');
    }
  } catch (error) {
    console.error('Park error:', error);
    toast.error('Error al aparcar carrito');
  }
}
```

### Flujo: Restaurar Carrito Aparcado

```
Usuario cliquea botón con contador de aparcados
         ↓
openParkedCartsModal()
  ├─ GET /parked/
  ├─ Llena parkedCarts[]
  └─ Abre modal

Usuario ve lista y cliquea "Recuperar"
         ↓
restoreParkedCart(parkedCartId)
  ├─ POST /carts/{parkedCartId}/restore/
  ├─ Backend elimina carrito activo anterior
  ├─ Backend marca como no-aparcado
  ├─ Backend genera nuevo session_id
  ├─ Frontend recibe items + session_id + activeCartId
  ├─ Frontend llena cart.value con items
  ├─ Frontend suscribe a nuevo canal
  ├─ Frontend recarga parkedCartsCount
  ├─ Modal se cierra
  └─ Toast "Carrito restaurado"
```

### Función: `restoreParkedCart()`

```typescript
async function restoreParkedCart(parkedCartId: string) {
  try {
    const response = await fetch(
      `/api/v1/carts/carts/${parkedCartId}/restore/`,
      {
        method: 'POST',
        headers: authHeaders
      }
    );
    
    const { success, data } = await response.json();
    
    if (success) {
      // Actualizar estado local
      cart.value = data.cart || [];
      activeCartId.value = data.active_cart_id;
      cartSessionId.value = data.session_id;
      cartTotal.value = data.total;
      
      // Suscribirse al nuevo canal
      subscribeToCartChannel(cartSessionId.value);
      
      // Recargar lista
      await loadParkedCartsCount();
      
      // Cerrar modal
      showParkedCartsModal.value = false;
      
      toast.success('Carrito restaurado exitosamente');
    }
  } catch (error) {
    console.error('Restore error:', error);
    toast.error('Error al restaurar carrito');
  }
}
```

### Subscripción a Pusher (Sincronización Real-time)

```typescript
function subscribeToCartChannel(sessionId: string) {
  // Desuscribirse del anterior si existe
  if (cartChannel) {
    pusher.unsubscribe(`private-cart-${cartSessionId.value}`);
  }
  
  // Suscribirse al nuevo canal
  const channelName = `private-cart-${sessionId}`;
  cartChannel = pusher.subscribe(channelName);
  
  cartChannel.bind('CART_UPDATED', (data: any) => {
    // Si fue update local, ignorar
    if (data.device_id === localDeviceId) {
      return;
    }
    
    // Si fue desde otro dispositivo, refetch silencioso
    console.log('Carrito actualizado desde otro dispositivo');
    loadActiveCart();  // GET /my-cart/ nuevamente
  });
}
```

---

## Flujos de Uso

### Caso 1: Un Cajero, Una Venta

```
1. Cajero A abre POS
2. GET /my-cart/ → carrito vacío, session_id = "device_A_123"
3. Agrega 3 productos → cart = [A, B, C]
4. POST /sync-cart/ → Backend persiste
5. Cliente paga → Procesa venta
6. Carrito se limpia automáticamente → cart = []
```

### Caso 2: Pausa y Retoma (Mismo Usuario)

```
Cajero A:
  1. Abre POS, agrega 3 productos → cart = [A, B, C]
  2. Cliente dice "Espérame un momento"
  3. Click "📌 Aparcar"
  4. POST /park/ → Carrito se guarda, nuevo carrito vacío
  
Cajero B (o A en otra pantalla):
  1. Abre POS en otra tablet
  2. GET /my-cart/ → carrito vacío (el nuevo)
  3. Atiende a otro cliente
  4. Agrega diferentes productos
  
Cajero A:
  1. Vuelve a su tablet
  2. Click en botón de aparcados
  3. GET /parked/ → ve su carrito [A, B, C]
  4. Click "Recuperar"
  5. POST /restore/ → Carrito [A, B, C] vuelve como activo
  6. Continúa atendiendo al cliente original
```

### Caso 3: Multi-dispositivo (Mismo Usuario)

```
Tablet 1 (Caja principal):
  - GET /my-cart/ → session_id = "device_abc_123"
  - Suscribe a private-cart-device_abc_123
  - Agrega Producto A
  - POST /sync-cart/ → Backend emite CART_UPDATED

Tablet 2 (Área de devoluciones, MISMO usuario):
  - GET /my-cart/ → session_id = "device_abc_123" (MISMO)
  - Suscribe a private-cart-device_abc_123 (MISMO canal)
  - Recibe evento CART_UPDATED → GET /my-cart/ → ve [A]
  
Tablet 1:
  - Agrega Producto B
  - POST /sync-cart/ → [A, B]
  
Tablet 2:
  - Recibe evento → GET /my-cart/ → ve [A, B]
  
Resultado: SINCRONIZACIÓN EN TIEMPO REAL ✅
```

---

## Archivos Modificados

### Backend

| Archivo | Cambios |
|---------|---------|
| `nurax_backend/apps/carts/models.py` | Campos `is_parked` y `parked_at` añadidos a `ActiveCart` |
| `nurax_backend/apps/carts/views.py` | Implementados endpoints: `park()`, `restore()`, `list_parked()` + Broadcasting |
| `nurax_backend/apps/carts/serializers.py` | Serialización de parked_at, is_parked |
| `nurax_backend/apps/carts/migrations/0002_add_parked_fields.py` | Migración: campos nuevos + índices |
| `nurax_backend/core/urls.py` | Ruta `/api/pusher/auth/` registrada |

### Frontend

| Archivo | Cambios |
|---------|---------|
| `nurax_inventario/src/components/SalesModal.vue` | Modal aparcados, botón "📌 Aparcar", lógica de restauración, Pusher subscription |

### Documentación

| Archivo | Propósito |
|---------|-----------|
| `nurax_backend/docs/CART_PARKING_SYSTEM.md` | Este documento |

---

## Testing

### Test Backend

**Crear carrito y agregar items:**
```bash
curl -X POST http://localhost:8000/api/v1/carts/carts/sync-cart/ \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=<tu_token>" \
  -d '{
    "device_id": "test_device_001",
    "cart": [
      {
        "id": "<product-uuid>",
        "quantity": 2,
        "sale_price": "15.50",
        "store": "<store-uuid>"
      }
    ]
  }'
```

**Obtener carrito activo:**
```bash
curl -X GET http://localhost:8000/api/v1/carts/carts/my-cart/ \
  -H "Cookie: access_token=<tu_token>"
```

**Aparcar carrito:**
```bash
curl -X POST http://localhost:8000/api/v1/carts/carts/<cart-uuid>/park/ \
  -H "Cookie: access_token=<tu_token>"
```

**Listar aparcados:**
```bash
curl -X GET http://localhost:8000/api/v1/carts/carts/parked/ \
  -H "Cookie: access_token=<tu_token>"
```

**Restaurar aparcado:**
```bash
curl -X POST http://localhost:8000/api/v1/carts/carts/<parked-cart-uuid>/restore/ \
  -H "Cookie: access_token=<tu_token>"
```

### Test Frontend

1. **Abrir DevTools** (F12) en navegador
2. **Autenticarse** como usuario con permisos de POS
3. **Abrir SalesModal** (POS)
4. **Agregar productos** desde inventario
5. **Ver sincronización** en Network tab
6. **Aparcar carrito** → Ver nuevo session_id
7. **Restaurar** → Ver items cargados
8. **Multi-dispositivo** → Abrir en otra pestaña, agregar producto, ver sync en tiempo real

---

## Notas Técnicas Importantes

### 🔑 Conceptos Clave

1. **Carrito Único Activo por Usuario/Tienda**
   - Un usuario solo tiene 1 carrito ACTIVO por tienda
   - Múltiples dispositivos leen el MISMO carrito (mismo session_id)
   - Aparcados NO cuentan como activos

2. **Session ID**
   - Generado por backend al crear carrito
   - Usado para canal Pusher: `private-cart-{session_id}`
   - Permite múltiples usuarios en mismo POS sin interferir

3. **Broadcasting Pusher**
   - Se emite DESPUÉS de upsert/park/restore
   - Otros dispositivos reciben evento y refetch
   - Ignoran si `device_id` es local

4. **Migración de BD**
   - Campos `is_parked` y `parked_at` ya aplicados
   - Índice en `(is_parked, user)` para búsquedas rápidas
   - NO rompe datos existentes (default=False)

### ⚠️ Limitaciones Actuales

- ❌ No hay límite de carritos aparcados por usuario
- ❌ No hay limpieza automática de carritos aparcados antiguos
- ❌ Pusher requiere autenticación (no anónimo)

### 🚀 Mejoras Futuras

- [ ] Agregar timestamp de último cambio en items
- [ ] Limpieza automática de aparcados después de X días
- [ ] Historial de cambios en carrito
- [ ] Notas/comentarios en carrito aparcado
- [ ] Compartir carrito entre múltiples usuarios (con permisos)

### 📝 Reglas de Negocio

1. **Aparcamiento:** Un carrito ACTIVO se puede aparcar (solo si tiene items)
2. **Restauración:** Un carrito aparcado puede restaurarse (vuelve a ACTIVO)
3. **Eliminación de anterior:** Al restaurar, carrito activo previo se elimina
4. **Sincronización:** El backend es fuente única de verdad
5. **Seguridad:** Solo usuario autenticado ve/modifica sus carritos

---

## Preguntas Frecuentes

### ¿Qué pasa si un usuario tiene múltiples pestañas abiertas?

Ambas pestañas comparten el MISMO session_id (obtenido en GET /my-cart/). Pusher envía evento a ambas. Evita conflictos mediante `device_id` check.

### ¿Se pierden items al aparcar?

NO. Los items se guardan en BD con el carrito. Al restaurar, vuelven con todos los datos.

### ¿Puede haber 2 carritos activos?

NO. El backend filtra `is_parked=False` para obtener activo. Si alguien intenta crear 2, el segundo reemplaza al primero.

### ¿Qué pasa si Pusher cae?

El sistema sigue funcionando. Solo falta sincronización real-time. Usuarios pueden refrescar manualmente.

### ¿El session_id cambia cada vez?

NO, es constante mientras el carrito está activo. Cambia solo cuando se restaura desde aparcado (para evitar conflictos).

---

## Diagrama de Estados del Carrito

```
┌──────────────────┐
│   NO EXISTE      │  GET /my-cart/ → []
└────────┬─────────┘
         │
         │ POST /sync-cart/ (agregar items)
         ↓
┌──────────────────┐
│   ACTIVO         │  ← Usuario viendo/editando
│ is_parked=False  │
└────────┬─────────┘
         │
         ├─► POST /park/          ↓ POST /sync-cart/ (vaciar items)
         │                            │
         │   ↓                         ↓
         │
    ┌─────────────────┐      ┌──────────────────┐
    │    APARCADO     │      │   ELIMINADO      │
    │  is_parked=True │      │  (no en BD)      │
    └────────┬────────┘      └──────────────────┘
             │
             │ POST /restore/
             ↓
    ┌──────────────────┐
    │   ACTIVO (nuevo) │
    │ is_parked=False  │
    │ session_id nuevo │
    └──────────────────┘
```

---

## Cómo Continuar el Desarrollo

### Para Agregar Nueva Feature

1. **Identifica si es backend o frontend:**
   - BD/lógica → Backend
   - UI/UX → Frontend
   
2. **Backend:**
   - Edita `models.py` si necesitas campos
   - Edita `views.py` para endpoints
   - Crea migración: `python manage.py makemigrations`
   - Emite Pusher si es necesario
   
3. **Frontend:**
   - Edita `SalesModal.vue`
   - Agrega función async para API
   - Actualiza estado local (refs)
   - Vincula a Pusher events si es necesario

4. **Testing:**
   - Prueba endpoint con curl
   - Prueba UI en navegador
   - Prueba multi-dispositivo si aplica

### Debugging

**Backend:**
- Logs: Busca `[CARTS]` en terminal Django
- Database: Ver carritos aparcados: `ActiveCart.objects.filter(is_parked=True)`

**Frontend:**
- Console: `console.log(cart, cartSessionId, activeCartId)`
- Network tab: Ver requests y responses
- Pusher console: Ver eventos en tiempo real

---

**FIN DE DOCUMENTACIÓN**

Última actualización: Mayo 7, 2026  
Autores: Equipo de Desarrollo  
Estado: ✅ Listo para producción
