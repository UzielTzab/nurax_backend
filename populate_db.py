import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nurax_backend.settings")
django.setup()

from api.models import User, Client, Category, Supplier, Product

def populate():
    print("Iniciando poblado de base de datos...")

    # 1. Crear usuario Admin
    admin_email = "admin@nurax.com"
    admin_pass  = "Admin123$secure"
    if not User.objects.filter(email=admin_email).exists():
        User.objects.create_superuser(
            email=admin_email,
            username="admin_nurax",
            password=admin_pass,
            name="Super Admin Nurax",
            role="admin"
        )
        print(f"✅ Admin creado: {admin_email}")

    # 2. Crear usuario Cliente de prueba
    client_email = "prueba@nurax.com"
    client_pass  = "Cliente123$secure"
    if not User.objects.filter(email=client_email).exists():
        cliente_user = User.objects.create_user(
            email=client_email,
            username="cliente_prueba",
            password=client_pass,
            name="Usuario de Prueba",
            role="cliente"
        )
        # Crear perfil Client para este User
        Client.objects.create(
            user=cliente_user,
            name="Usuario de Prueba",
            email=client_email,
            company="Nurax Testing Corp",
            plan="pro",
            active=True
        )
        print(f"✅ Cliente de prueba creado: {client_email}")

    # 3. Datos generales (Categorías)
    cats = ['Laptops', 'Smartphones', 'Accesorios', 'Servidores']
    cat_objs = {}
    for c in cats:
        cat_obs, created = Category.objects.get_or_create(name=c)
        cat_objs[c] = cat_obs
        if created:
            print(f"   Categoria creada: {c}")

    # 4. Proveedores
    sup_mail = "contacto@techsupply.com"
    if not Supplier.objects.filter(email=sup_mail).exists():
        sup = Supplier.objects.create(
            name="Tech Supply Global",
            email=sup_mail,
            phone="+1234567890",
            company="Tech Supply LLC"
        )
        print("✅ Proveedor creado")
    else:
        sup = Supplier.objects.get(email=sup_mail)

    # 5. Productos
    sku_list = ['LAP-001', 'SMART-X1', 'ACC-MOUSE-01']
    if not Product.objects.filter(sku='LAP-001').exists():
        Product.objects.create(
            name="MacBook Pro 16",
            category=cat_objs['Laptops'],
            supplier=sup,
            sku="LAP-001",
            stock=15,
            price=Decimal("2500.00")
        )
        Product.objects.create(
            name="iPhone 15 Pro",
            category=cat_objs['Smartphones'],
            supplier=sup,
            sku="SMART-X1",
            stock=30,
            price=Decimal("999.00")
        )
        Product.objects.create(
            name="Logitech MX Master 3",
            category=cat_objs['Accesorios'],
            supplier=sup,
            sku="ACC-MOUSE-01",
            stock=100,
            price=Decimal("99.99")
        )
        print("✅ Productos de prueba creados")

    print("🎉 Poblado finalizado exitosamente!")
    print("-" * 40)
    print("CUENTAS DE ACCESO:")
    print(" 🛠️ Rol: ADMIN")
    print(f"    - Email: {admin_email}")
    print(f"    - Contraseña: {admin_pass}")
    print("\n 🏢 Rol: CLIENTE")
    print(f"    - Email: {client_email}")
    print(f"    - Contraseña: {client_pass}")
    print("-" * 40)

if __name__ == "__main__":
    populate()
