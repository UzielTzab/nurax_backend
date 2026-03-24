# Nurax Backend - API y Base de Datos

Backend desarrollado con Django REST Framework y PostgreSQL, contenerizado con Docker.

## Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.12+ (opcional, si ejecutas localmente)

## Configuración Inicial

### 1. Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables (opcional, tienen valores por defecto):

```env
# Base de Datos
DB_NAME=nurax_db
DB_USER=nurax_user
DB_PASSWORD=nurax_password

# Cloudinary (opcional)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# Pusher (opcional)
PUSHER_APP_ID=tu_app_id
PUSHER_KEY=tu_key
PUSHER_SECRET=tu_secret
PUSHER_CLUSTER=tu_cluster
```

## Construcción y Levantamiento de Contenedores

### Construir la imagen y levantar los contenedores

```bash
docker-compose up --build
```

Este comando:
- Construye la imagen de la API
- Levanta los contenedores de la API y la base de datos
- Ejecuta automáticamente las migraciones
- Ejecuta el script `init_db.py`
- Inicia el servidor Django en `http://localhost:8000`

### Levantar contenedores (sin reconstruir)

```bash
docker-compose up
```

### Detener los contenedores

```bash
docker-compose down
```

### Detener y eliminar volúmenes (borrar base de datos)

```bash
docker-compose down -v
```

## Acceso a los Contenedores

### Acceder al contenedor de la API (bash)

```bash
docker exec -it nurax_api bash
```

### Acceder al contenedor de la base de datos (PostgreSQL)

```bash
docker exec -it nurax_db psql -U nurax_user -d nurax_db
```

### Ver logs del contenedor de la API

```bash
docker logs -f nurax_api
```

### Ver logs de la base de datos

```bash
docker logs -f nurax_db
```

## Comandos de Django

Todos estos comandos deben ejecutarse dentro del contenedor de la API usando `docker exec`.

### Ejecutar migraciones

```bash
docker exec nurax_api python manage.py migrate
```

### Crear migraciones

```bash
docker exec nurax_api python manage.py makemigrations
```

### Ver el estado de las migraciones

```bash
docker exec nurax_api python manage.py showmigrations
```

### Deshacer una migración

```bash
docker exec nurax_api python manage.py migrate <app_name> <numero_migracion>
```

Ejemplo:
```bash
docker exec nurax_api python manage.py migrate api 0001
```

### Crear un superusuario

```bash
docker exec -it nurax_api python manage.py createsuperuser
```

### Ejecutar el script de inicialización de base de datos

```bash
docker exec nurax_api python init_db.py
```

### Ejecutar el script de población de datos

```bash
docker exec nurax_api python populate_db.py
```

### Abrir la consola interactiva de Django

```bash
docker exec -it nurax_api python manage.py shell
```

## Acceso a la API

- **API Base URL**: `http://localhost:8000`
- **Admin Panel**: `http://localhost:8000/admin`
- **Documentación API**: Depende de tu configuración de drf-spectacular

## Acceso a la Base de Datos

- **Host**: `localhost`
- **Puerto**: `5432`
- **Usuario**: `nurax_user` (configurable)
- **Contraseña**: `nurax_password` (configurable)
- **Base de datos**: `nurax_db` (configurable)

### Conectar desde una herramienta externa (pgAdmin, DBeaver, etc.)

```
Host: localhost
Port: 5432
Database: nurax_db
Username: nurax_user
Password: nurax_password
```

## Desarrollo

### Recargar el servidor sin reconstruir

El servidor se recarga automáticamente cuando cambias archivos Python (gracias a los volúmenes montados).

### Instalar nuevas dependencias

1. Agrega el paquete a `requirements.txt`
2. Reconstruye la imagen:

```bash
docker-compose up --build
```

O, si ya está corriendo:

```bash
docker exec nurax_api pip install -r requirements.txt
```

## Troubleshooting

### El contenedor no inicia

Verifica los logs:
```bash
docker logs nurax_api
docker logs nurax_db
```

### Error de conexión a la base de datos

Asegúrate de que:
- El contenedor `nurax_db` está corriendo: `docker ps`
- Las variables de entorno son correctas
- El puerto 5432 no está ocupado por otra aplicación

### Limpiar el proyecto y empezar de nuevo

```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## Estructura del Proyecto

```
nurax_backend/
├── manage.py           # Script de gestión de Django
├── requirements.txt    # Dependencias de Python
├── dockerfile          # Configuración de Docker
├── docker-compose.yml  # Configuración de servicios
├── init_db.py         # Script de inicialización
├── populate_db.py     # Script de población de datos
├── db.sqlite3         # Base de datos local (ignorar)
├── api/               # Aplicación Django principal
│   ├── models.py      # Modelos de datos
│   ├── views.py       # Vistas/ViewSets
│   ├── serializers.py # Serializadores
│   ├── urls.py        # URLs
│   └── migrations/    # Migraciones de base de datos
└── nurax_backend/     # Configuración del proyecto
    ├── settings.py    # Configuración de Django
    ├── urls.py        # URLs principales
    └── wsgi.py        # Configuración WSGI
```

## Notas Importantes

- El archivo `.env` no debe ser versionado. Asegúrate de que está en `.gitignore`
- En producción, cambia `DEBUG=False` y actualiza `SECRET_KEY`
- Las credenciales de Cloudinary y Pusher son opcionales para desarrollo local
- Los datos de la base de datos se persisten en el volumen `postgres_data`
