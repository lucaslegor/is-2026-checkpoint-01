# TeamBoard App — IS-2026 Checkpoint 01

Aplicación web que muestra los integrantes del equipo, la feature que implementó cada uno y el estado de su servicio. El frontend solicita los datos al backend, el backend los lee de la base de datos, y todo corre orquestado por Docker Compose.

---

## Integrantes

| Nombre             | Legajo | Feature    | Servicio                        |
|--------------------|--------|------------|---------------------------------|
| Legorburu Lucas    |        | Feature 01 | Infraestructura y coordinación  |
| Bellizi Tomás      |        | Feature 02 | Frontend (HTML + JS)            |
| Giordani Luca      |        | Feature 03 | Backend (Flask API)             |
| Devida Facundo     |        | Feature 04 | Base de datos (PostgreSQL)      |
| Rodriguez Joaquín  |        | Feature 05 | Panel de monitoreo (Portainer)  |
| Piquet Leonel      |        | Feature 06 | Administración BD (pgAdmin)     |

---

## Arquitectura

```
Navegador
│
├── :8080 → frontend   (Python http.server + HTML/JS)   ← Feature 02
│              │
│              └── fetch() a :5000/api/team
│
├── :5000 → backend    (Flask API)                       ← Feature 03
│              │
│              └── SELECT * FROM members
│
│           database   (PostgreSQL — sin puerto público) ← Feature 04
│
├── :9000 → portainer  (panel de monitoreo Docker)       ← Feature 05
│
└── :5050 → pgadmin    (administración de la BD)         ← Feature 06
```

---

## Servicios

| Servicio  | Imagen / Build              | Puerto | Descripción                                      |
|-----------|-----------------------------|--------|--------------------------------------------------|
| database  | postgres:16-alpine          | —      | Base de datos PostgreSQL.                        |
| backend   | ./backend (Dockerfile)      | 5000   | API REST Flask. Expone `/api/team`, `/api/health`, `/api/info`. |
| frontend  | ./frontend (Dockerfile)     | 8080   | Servidor estático Python. Sirve `index.html` y `app.js`. |
| portainer | portainer/portainer-ce:latest | 9000 | Panel web para monitorear los contenedores Docker. |
| pgadmin   | dpage/pgadmin4              | 5050   | Interfaz web para administrar la base de datos.  |

---

## Requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado y corriendo
- [Docker Compose](https://docs.docker.com/compose/) (incluido en Docker Desktop)

---

## Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/LucasLegorburu/is-2026-checkpoint-01.git
cd is-2026-checkpoint-01
```

### 2. Configurar las variables de entorno

```bash
cp .env.example .env
```

Editar el archivo `.env` con los valores reales:

```bash
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
BACKEND_PORT=
FRONTEND_PORT=
PORTAINER_PORT=
PGADMIN_EMAIL=
PGADMIN_PASSWORD=
```

### 3. Levantar los servicios

```bash
docker compose up -d --build
```

### 4. Verificar que todo esté corriendo

```bash
docker compose ps
```

Todos los servicios deben aparecer en estado `running`.

---

## Acceso a los servicios

| Servicio  | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:8080      |
| Backend   | http://localhost:5000      |
| Portainer | http://localhost:9000      |
| pgAdmin   | http://localhost:5050      |

> La primera vez que se abre Portainer solicita crear un usuario administrador.

---

## Comandos útiles

```bash
# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f backend

# Bajar todos los servicios
docker compose down

# Bajar y borrar volúmenes (resetea la base de datos)
docker compose down -v

# Reiniciar un servicio
docker compose restart backend
```

---

## Estructura del repositorio

```
is-2026-checkpoint-01/
│
├── docker-compose.yml       ← orquesta todos los servicios
├── .env                     ← variables de entorno (no va a git)
├── .env.example             ← plantilla sin valores reales
├── .gitignore               ← excluye .env y archivos locales
├── README.md                ← este archivo
│
├── frontend/                ← Feature 02
│   ├── Dockerfile
│   ├── .dockerignore
│   └── html/
│       ├── index.html
│       ├── app.js
│       └── syles.css
│
├── backend/                 ← Feature 03
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── app.py
│
├── database/                ← Feature 04
│   └── init.sql
│
└── portainer/               ← Feature 05 (configurado en compose)
```
---

## Feature 01 — Coordinación e Infraestructura Base

**Responsable:** Legorburu Lucas

Esta feature es el punto de partida del proyecto. Incluye:

- Creación del repositorio en GitHub con el nombre `is-2026-checkpoint-01`
- Configuración de branch protection en `main` (todo entra por Pull Request)
- Invitación de los compañeros como colaboradores
- Creación de la estructura de carpetas vacías del proyecto
- **`docker-compose.yml`** — orquesta los 4 servicios (database, backend, frontend, portainer)
- **`.env`** — variables de entorno con valores reales (no va a git)
- **`.env.example`** — plantilla sin valores para que los compañeros sepan qué configurar
- **`.gitignore`** — excluye `.env` y archivos locales del repositorio
- Revisión y merge de los Pull Requests de los demás integrantes
- Verificación final de que `docker compose up` levanta todo sin errores
- Escritura del `README.md` completo

### Decisiones tomadas en el `docker-compose.yml`

**Red interna `teamboard-net`:** todos los servicios comparten una red bridge interna. Los servicios se encuentran entre sí por nombre (`database`, `backend`, etc.) sin necesidad de exponer puertos innecesarios.

**La base de datos no expone puerto al host:** PostgreSQL solo es accesible desde el backend por la red interna. El backend usa `POSTGRES_HOST=database` para conectarse.

**`depends_on` con `condition: service_healthy` en el backend:** el backend espera a que el `healthcheck` de la base de datos (`pg_isready`) devuelva OK antes de arrancar. Esto evita errores de conexión en el arranque.

**Volúmenes nombrados para persistencia:** `database_data` y `portainer_data` son volúmenes gestionados por Docker. Los datos persisten aunque los contenedores sean destruidos y recreados.

**Bind mount de `init.sql`:** el script de inicialización de la base de datos se monta en `/docker-entrypoint-initdb.d/` para que PostgreSQL lo ejecute automáticamente la primera vez.

**Límites de recursos en todos los servicios:** se definen `cpus` y `memory` para evitar que un contenedor consuma todos los recursos del host.

---

## Feature 02 — Frontend (HTML + JS)

**Responsable:** Bellizzi Tomás

Esta feature implementa la interfaz web de TeamBoard. Incluye:

- **`frontend/Dockerfile`** — construye la imagen a partir de `python:3.12-slim` y levanta un servidor HTTP con `python3 -m http.server` en el puerto 8080 sirviendo el directorio `html/`.
- **`frontend/.dockerignore`** — excluye archivos innecesarios del contexto de build.
- **`frontend/html/index.html`** — estructura visual de la página: encabezado con el nombre del grupo y tabla de integrantes.
- **`frontend/html/app.js`** — lógica del cliente: `fetch()` al backend en `/api/team`, construcción dinámica de filas y badge de estado; indicador de si el backend responde.
- **`frontend/html/syles.css`** — estilos de la interfaz.

### Decisiones tomadas en el frontend

**Python `http.server` como servidor estático:** no se requiere Nginx ni ningún servidor web complejo. El intérprete de Python incluye un servidor HTTP suficiente para servir archivos estáticos con un solo comando.

**Tabla construida dinámicamente con JavaScript:** los datos de los integrantes no están escritos en el HTML sino que se obtienen en tiempo de ejecución desde el backend. El frontend refleja el estado real de la base de datos.

**Indicador de estado del backend:** si el backend no responde, la página muestra un mensaje de error visible en lugar de una tabla vacía, facilitando la detección de problemas en el entorno.

**Imagen base `python:3.12-slim` con versión fija:** se evita `latest` para garantizar reproducibilidad del build, y se usa la variante slim para reducir el tamaño de la imagen.

**`BACKEND_URL` en `app.js`:** por defecto apunta a `http://localhost:5000/api/team`. Si se cambia `BACKEND_PORT` en `.env`, hay que actualizar esa constante para que el navegador use el puerto correcto.

---

## Feature 03 — Backend (Flask API)

**Responsable:** Giordani Luca

Esta feature expone la API REST que consume el frontend y consulta PostgreSQL. Incluye:

- **`backend/app.py`** — aplicación Flask con CORS, conexión a PostgreSQL mediante `psycopg2`, endpoints `GET /api/health`, `GET /api/team` y `GET /api/info`, manejadores 404/500 y logging.
- **`backend/requirements.txt`** — Flask, Flask-CORS, psycopg2-binary, python-dotenv y gunicorn.
- **`backend/Dockerfile`** — imagen `python:3.12-slim`, instalación de dependencias y `curl` para el healthcheck, usuario no root, HEALTHCHECK contra `/api/health`, arranque con Gunicorn (`--workers 2`) en `0.0.0.0:5000`.
- **`backend/.dockerignore`** — reduce el contexto de build.

### Decisiones tomadas en el backend

**Configuración por variables de entorno:** usuario, contraseña, base y host (`POSTGRES_HOST=database` en Compose) evitan credenciales en el código y alinean el contenedor con el servicio `database`.

**Gunicorn en contenedor:** se usa un servidor WSGI adecuado para producción en lugar de `app.run` en modo debug.

**CORS habilitado:** el frontend se sirve en otro origen (puerto distinto); `Flask-CORS` permite las peticiones `fetch` desde el navegador.

**Healthcheck HTTP:** el contenedor expone `/api/health` para que Docker verifique que el servicio sigue respondiendo.

---

## Feature 04 — Base de datos (PostgreSQL)

**Responsable:** Devida Facundo

Esta feature define el modelo de datos y los datos semilla del equipo. Incluye:

- **`database/init.sql`** — creación de la tabla `members` (`id`, `nombre`, `apellido`, `legajo`, `feature`, `servicio`, `estado` con `CHECK` en `ACTIVO` / `INACTIVO`) e inserción de los seis integrantes.
- **Servicio `database` en `docker-compose.yml`** — imagen `postgres:16-alpine`, variables desde `.env`, volumen `database_data`, healthcheck con `pg_isready`, montaje de `init.sql` en `/docker-entrypoint-initdb.d/` para que PostgreSQL lo ejecute automáticamente la primera vez que el volumen está vacío.

### Decisiones tomadas en la base de datos

**Sin puerto publicado al host:** PostgreSQL solo es accesible desde la red Docker (por ejemplo el backend y pgAdmin), lo que reduce la exposición innecesaria en desarrollo local.

**PostgreSQL 16 Alpine:** imagen oficial ligera con versión explícita para alinear entornos entre integrantes.

**Restricciones en el esquema:** `legajo` único y valores permitidos en `estado` mantienen consistencia de los datos del equipo.

---

## Feature 05 — Panel de Monitoreo (Portainer)
  **Responsable:** Rodriguez Joaquín

  Esta feature agrega un panel web para monitorear y gestionar los contenedores Docker del proyecto en tiempo real. Incluye:

  - **`docker-compose.yml`** — agrega el servicio `portainer` con su imagen oficial y el volumen persistente `portainer_data`
  - **`portainer/`** — carpeta del servicio con `.gitignore` para excluir datos locales generados por Portainer
  - **`.env.example`** — agrega la variable `PORTAINER_PORT` para que cada integrante configure su puerto local

  ### Decisiones tomadas en el servicio Portainer

  **Imagen `portainer/portainer-ce:2.27.0` con versión fija:** se evita `latest` para garantizar que todos los integrantes del equipo levanten
  exactamente la misma versión del panel, evitando diferencias de comportamiento entre entornos.

  **Bind mount de `/var/run/docker.sock`:** Portainer necesita acceso al socket de Docker del host para poder listar y gestionar los contenedores. Es el 
  mecanismo estándar para que un contenedor interactúe con el daemon de Docker.

  **Volumen nombrado `portainer_data`:** la configuración de Portainer (usuarios, contraseñas, endpoints) se persiste en un volumen gestionado por       
  Docker. Esto evita tener que reconfigurar el panel cada vez que el contenedor es recreado.

  **Sin `depends_on`:** Portainer no depende de ningún otro servicio para arrancar. Puede levantarse en cualquier orden ya que solo interactúa con el    
  daemon de Docker, no con los demás contenedores de la red.

  **Integrado a la red `teamboard-net`:** aunque Portainer no necesita comunicarse con los otros servicios por red, unirse a la misma red interna le     
  permite visualizarlos correctamente en el panel.
  ## Acceso a Portainer

  1. Abrí el navegador en `http://localhost:9000`
  2. La primera vez te va a pedir crear un usuario administrador:
     - **Username:** el que vos elijas (ej: `admin`)
     - **Password:** mínimo 12 caracteres
  3. Hacé clic en **Create user**
  4. En la siguiente pantalla seleccioná **Get Started**
  5. Hacé clic en **local** para ver los contenedores del host
<img width="1601" height="326" alt="image" src="https://github.com/user-attachments/assets/d0fd8ce8-4cbf-4126-88fa-dc319374ba1b" />

---

## Feature 06 — Administración BD (pgAdmin)

**Responsable:** Piquet Leonel

Esta feature agrega una interfaz web para administrar PostgreSQL sin depender de un cliente instalado en el host. Incluye:

- **`docker-compose.yml`** — servicio `pgadmin` con imagen `dpage/pgadmin4:8.5`, variables `PGADMIN_DEFAULT_EMAIL` y `PGADMIN_DEFAULT_PASSWORD` tomadas desde `.env`, mapeo de puerto `5050:80`, `depends_on` con `condition: service_healthy` sobre `database`, red `teamboard-net` y límites de recursos.
- **`.env.example`** — variables `PGADMIN_EMAIL` y `PGADMIN_PASSWORD` para el primer inicio de sesión en la interfaz.

### Decisiones tomadas en el servicio pgAdmin

**Imagen `dpage/pgadmin4:8.5` con versión fija:** mismo criterio que en el resto del stack para evitar diferencias entre entornos al usar `latest`.

**Esperar a la base sana:** `depends_on` con `condition: service_healthy` evita que pgAdmin arranque antes de que PostgreSQL acepte conexiones.

**Acceso a la base desde la UI:** al registrar el servidor en pgAdmin, el host es el nombre del servicio Docker `database`, puerto `5432`, con usuario, contraseña y base definidos en `.env`.

**Puerto fijo en el compose:** el mapeo `5050:80` expone la interfaz en `http://localhost:5050` de forma consistente para todo el equipo.
