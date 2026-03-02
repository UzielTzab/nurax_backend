import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nurax_backend.settings")
django.setup()

from api.models import Category, User

print("--- Iniciando poblado de base de datos de producción ---")

# 1. Crear las Categorías Base Exactas
categorias = [
    'Laptop', 'Smartphone', 'Audio', 'Wearable', 
    'Fotografía', 'Gaming', 'Accesorios', 'Otros'
]
for c in categorias:
    obj, created = Category.objects.get_or_create(name=c)
    status = "Creada" if created else "Ya existía"
    print(f"[{status}] Categoría: {c}")

# 2. Crear Superusuario Maestro de Producción (Variables de entorno)
email_admin = os.environ.get('ADMIN_EMAIL', 'uzieltzab8@gmail.com')
password_admin = os.environ.get('ADMIN_PASSWORD')

if not password_admin:
    print("[Aviso] No se definió ADMIN_PASSWORD en el entorno. Saltando creación del Superusuario para no interrumpir el inicio del servidor.")
else:
    if not User.objects.filter(email=email_admin).exists():
        User.objects.create_superuser(
            username='admin_produccion', 
            email=email_admin, 
            password=password_admin,
            name='Administrador Maestro',
            role='admin',
            is_active=True
        )
        print(f"[Creado] Superusuario maestro '{email_admin}' creado con éxito.")
    else:
        print(f"[Aviso] El superusuario '{email_admin}' ya existe en la base de datos.")

print("--- Finalizado ---")
