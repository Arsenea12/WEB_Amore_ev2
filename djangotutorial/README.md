# Amore Di Ramos

Aplicación web desarrollada con **Django** para una floristería


## Descripción

Proyecto de evaluación del módulo *Desarrollo de aplicaciones del lado del servidor con Django e Inteligencia Artificial* (Evaluación 2: Django Admin y CRUD).

La aplicación es el sitio de una floristería con dos partes:
- **Encuestas**: los visitantes pueden votar por sus preferencias (una vez por sesión de navegador, con restricción anti-fraude).
- **Catálogo de productos**: gestión completa (crear, editar, eliminar) de ramos/arreglos, protegida por login y restringida a usuarios **staff**.

Incluye registro público de usuarios, un panel de administración de Django personalizado, y JavaScript del lado del cliente para mejorar la experiencia de uso.

## Tecnologías utilizadas

- Python 3 / Django Framework
- **MySQL 8.4** — única base de datos del proyecto, corre en un contenedor Docker
- Docker y Docker Compose
- HTML5, CSS3, JavaScript
- django-debug-toolbar
- Inteligencia Artificial como apoyo al desarrollo

## Uso de Inteligencia Artificial en el desarrollo

Apoyo al diseño de interfaces: se usó GitHub Copilot para organizar y comentar CSS/HTML por secciones, y para proponer la asignación cíclica de imágenes con {% cycle %} en las tarjetas de encuestas. Cada sugerencia se validó ejecutando el servidor local y revisando visualmente el resultado; lo que generaba errores o no calzaba con el estilo del sitio se corrigió a mano.

Generación de datos de prueba: las 6 preguntas de encuesta y sus opciones se generaron con IA a partir de un prompt del tipo: "Genera 6 preguntas de encuesta para una floristería de lujo llamada Amore Di Ramos, con 3-4 opciones cada una, en español, sobre preferencias de flores, ocasiones y estilos de entrega." Se validaron manualmente el largo de texto, el tono y que no hubiera duplicados, y se cargan mediante un comando propio (`cargar_encuestas`, ver más abajo).

## Protocolos, servicios de hosting y dominios

El proyecto corre empaquetado en contenedores Docker (`db` para MySQL, `web` para Django), comunicándose por HTTP dentro de una red interna de Docker y expuesto a `http://localhost:8000/`. El archivo `wsgi.py` es el punto de entrada para un servidor de producción (Gunicorn/uWSGI) dentro del contenedor `web`.

Gracias a Docker, el despliegue a un hosting real se simplifica: cualquier proveedor que soporte contenedores (Render, Railway, un VPS con Docker instalado) puede correr la misma imagen sin reconfigurar nada del código, más allá de ajustar las variables de entorno de producción (`DEBUG=False`, `ALLOWED_HOSTS` con el dominio real, credenciales de base de datos) y apuntar los registros DNS del dominio al servidor donde quede alojado.

## Funcionalidades principales

- **Encuestas**: listado, detalle y votación, con restricción de un voto por encuesta por sesión (`request.session`).
- **Catálogo de productos (CRUD)**: listar y ver el detalle son públicos; crear, editar y eliminar requieren sesión iniciada **y** permiso de staff (`StaffRequiredMixin`).
- **Autenticación**:
  - Login / logout (`/accounts/login/`, `/accounts/logout/`).
  - Registro público (`/registro/`): cualquier visitante puede crear su cuenta; queda logueado automáticamente, pero **sin** permisos de staff (no puede tocar el catálogo).
  - Solo un administrador puede otorgar permisos de staff, desde `/admin/` → Usuarios.
- **JavaScript (`main.js`)**: filtro en vivo del catálogo por nombre/tipo, y confirmación antes de eliminar un producto. No reemplaza la seguridad del backend, solo mejora la experiencia.
- **Panel de administración personalizado**: estilo propio (colores, tipografías, imagen decorativa) en vez del admin por defecto de Django.
- **Comando de datos de prueba**: `docker compose exec web python manage.py cargar_encuestas` carga las 6 encuestas de ejemplo (generadas con IA) en la base de datos.

## Estructura del proyecto (MVC)

| Componente | Descripción |
|------------|-------------|
| **Models** | `Question`/`Choice` (encuestas) y `Producto` (catálogo) |
| **Views**  | CRUD de `Producto` (ListView, DetailView, CreateView, UpdateView, DeleteView con `StaffRequiredMixin`), vistas de encuestas, `login`/`logout`/`registro` |
| **Templates** | `base.html` con herencia, formularios propios para productos, login y registro, admin personalizado |

## Base de datos: MySQL en Docker

El proyecto usa **MySQL 8.4 como única base de datos**, corriendo en su propio contenedor Docker — no requiere instalar MySQL, XAMPP ni nada más en tu máquina, solo Docker.

Con [Docker Desktop](https://www.docker.com/) instalado, desde la carpeta raíz del proyecto (donde está `docker-compose.yml`):

```
docker compose up --build
```

Esto levanta dos contenedores conectados entre sí:
- **`db`**: MySQL 8.4, con sus datos guardados en un volumen de Docker (persisten aunque apagues el contenedor).
- **`web`**: la app Django, que espera a que `db` esté lista, aplica las migraciones automáticamente, y sirve la app en `http://localhost:8000/`.

Para crear un superusuario dentro del contenedor:
```
docker compose exec web python manage.py createsuperuser
```

Con esa cuenta puedes entrar tanto al sitio (`http://localhost:8000/`) como al panel de administración (`http://localhost:8000/admin/`).

Para cargar las encuestas de ejemplo:
```
docker compose exec web python manage.py cargar_encuestas
```

Puedes copiar `.env.example` a `.env` en la raíz del proyecto para personalizar el nombre de la base, usuario y contraseñas que usa `docker-compose.yml`.

Para ver el contenido de la base de datos directamente (más allá del panel `/admin/`):
```
docker compose exec db mysql -u django_user -p amore_di_ramos
```

Para apagar los contenedores cuando termines:

```
docker compose down
```

Si además quieres borrar los datos guardados en la base (usuarios, encuestas, productos que hayas creado), use `-v`:

```
docker compose down -v
```

## Cómo ejecutar el proyecto (resumen rápido)

```
# Requisito: tener Docker Desktop instalado y corriendo

# 1. Desde la carpeta raíz del proyecto (donde está docker-compose.yml)
docker compose up --build

# 2. En otra terminal, crear un superusuario
docker compose exec web python manage.py createsuperuser

# 3. Cargar las encuestas de ejemplo
docker compose exec web python manage.py cargar_encuestas

# 4. Abrir el navegador en http://localhost:8000/
```
