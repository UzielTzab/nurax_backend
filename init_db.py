import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nurax_backend.settings")
django.setup()

from api.models import Category, User

# Create categories
for c in ['Audio', 'Laptop', 'Smartphone', 'Wearable', 'Photography', 'Gaming', 'Accessories']:
    Category.objects.get_or_create(name=c)

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superuser 'admin' created with password 'admin123'")
else:
    print("Superuser 'admin' already exists")
