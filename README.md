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
| database  | postgres:16-alpine          | —      | Base de datos PostgreSQL. Sin puerto público.    |
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
POSTGRES_PASSWORD=una_contraseña_segura
POSTGRES_DB=
BACKEND_PORT=
FRONTEND_PORT=
PORTAINER_PORT=
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
│       └── app.js
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
**Responsable**: Bellizzi Tomás
Esta feature implementa la interfaz web de TeamBoard. Incluye:

Dockerfile — construye la imagen del frontend a partir de python:3.12-slim y levanta un servidor HTTP con python3 -m http.server 8080
.dockerignore — excluye archivos innecesarios del contexto de build
html/index.html — estructura visual de la página: encabezado con el nombre del grupo y tabla de integrantes
html/app.js — lógica del cliente: realiza un fetch() al backend en /api/team y construye la tabla dinámicamente con los datos recibidos. También muestra un indicador de estado según si el backend responde o no.

Decisiones tomadas en el frontend
Python http.server como servidor estático: no se requiere Nginx ni ningún servidor web complejo. El intérprete de Python incluye un servidor HTTP listo para usar con un solo comando, suficiente para servir archivos estáticos.
Tabla construida dinámicamente con JavaScript: los datos de los integrantes no están escritos en el HTML sino que se obtienen en tiempo de ejecución desde el backend. Esto garantiza que el frontend siempre refleja el estado real de la base de datos.
Indicador de estado del backend: si el backend no responde, la página muestra un mensaje de error visible en lugar de una tabla vacía, facilitando la detección de problemas en el entorno.
Imagen base python:3.12-slim con versión fija: se evita latest para garantizar reproducibilidad del build, y se usa la variante slim para reducir el tamaño de la imagen.

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

