"""
Script de debug para verificar permisos y StoreMembership.
Ejecutar con: python manage.py shell < debug_permissions.py
"""

from apps.accounts.models import User, Store, StoreMembership
from apps.products.models import Product

# Tu información desde el response de /me/
user_id = "d5f70ed9-68f1-4a34-934e-5324e9a9cc92"
store_id_from_payload = "cf6c1185-1b4d-4b2c-9c09-a8ac04764a82"

print("=" * 80)
print("DEBUG: Verificación de Permisos y StoreMembership")
print("=" * 80)

# 1. Verificar que el usuario existe
print("\n1. Verificando usuario...")
try:
    user = User.objects.get(id=user_id)
    print(f"✅ Usuario encontrado: {user.username} ({user.email})")
    print(f"   ID: {user.id}")
    print(f"   Role: {user.role}")
    print(f"   is_active: {user.is_active}")
except User.DoesNotExist:
    print(f"❌ Usuario NO encontrado con ID: {user_id}")

# 2. Verificar que la tienda existe
print("\n2. Verificando tienda...")
try:
    store = Store.objects.get(id=store_id_from_payload)
    print(f"✅ Tienda encontrada: {store.name}")
    print(f"   ID: {store.id}")
    print(f"   Plan: {store.plan}")
    print(f"   Active: {store.active}")
except Store.DoesNotExist:
    print(f"❌ Tienda NO encontrada con ID: {store_id_from_payload}")

# 3. Verificar StoreMembership
print("\n3. Verificando StoreMembership...")
user = User.objects.get(id=user_id)
memberships = StoreMembership.objects.filter(user=user)
print(f"   Membresías totales del usuario: {memberships.count()}")

for membership in memberships:
    print(f"\n   📍 Tienda: {membership.store.name}")
    print(f"      Store ID: {membership.store.id}")
    print(f"      Role: {membership.role}")
    print(f"      Created: {membership.created_at}")
    
    # Verificar si coincide con la tienda del payload
    if str(membership.store.id) == store_id_from_payload:
        print(f"      ✅ ESTA ES LA TIENDA DEL PAYLOAD")
    else:
        print(f"      ❌ NO es la tienda del payload")

# 4. Verificar directamente la combinación user+store
print("\n4. Verificando combinación user+store específica...")
try:
    store_obj = Store.objects.get(id=store_id_from_payload)
    specific_membership = StoreMembership.objects.get(user=user, store=store_obj)
    print(f"✅ StoreMembership EXISTE para esta combinación")
    print(f"   Role: {specific_membership.role}")
except StoreMembership.DoesNotExist:
    print(f"❌ StoreMembership NO EXISTE para esta combinación")
    print(f"   Usuario: {user.username}")
    print(f"   Tienda ID: {store_id_from_payload}")

# 5. Verificar productos existentes en esa tienda
print("\n5. Productos existentes en esa tienda...")
products = Product.objects.filter(store_id=store_id_from_payload)
print(f"   Cantidad de productos: {products.count()}")
for product in products[:5]:
    print(f"   - {product.name} (creado: {product.created_at})")

# 6. Resumen final
print("\n" + "=" * 80)
print("RESUMEN DE DIAGNÓSTICO:")
print("=" * 80)

try:
    user = User.objects.get(id=user_id)
    store = Store.objects.get(id=store_id_from_payload)
    membership_exists = StoreMembership.objects.filter(user=user, store=store).exists()
    
    if membership_exists:
        print("✅ TODO OK: Usuario está autenticado y tiene acceso a la tienda")
        print("   El error DEBERÍA haberse resuelto")
    else:
        print("❌ PROBLEMA: Usuario autenticado pero SIN acceso a la tienda")
        print("   StoreMembership NO EXISTE")
        print("\n   Opciones:")
        print("   1. La membresía se eliminó accidentalmente")
        print("   2. El UUID de tienda en el payload es incorrecto")
        print("   3. Hay un problema con las migraciones")
        
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 80)
