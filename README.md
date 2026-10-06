# SA — Pipeline CI/CD para API REST (Flask + Docker + GitHub Actions + AWS EC2)

API REST en **Python/Flask** con **6 endpoints**, **31 pruebas** con **pytest** (cobertura del 99 %,
umbral mínimo exigido: 70 %) y un pipeline de **GitHub Actions** que en cada `git push` a `main`:

1. corre lint y pruebas, y muestra la cobertura en los logs;
2. construye la imagen Docker y la publica en **Docker Hub** con los tags `:latest` y `:<sha del commit>`;
3. se conecta por **SSH** a una instancia **AWS EC2 (Ubuntu)**, descarga la imagen nueva, la valida,
   detiene el contenedor antiguo y levanta la versión nueva en el **puerto 80**.

## Arquitectura

```
 Desarrollador ──git push──► GitHub (rama main)
                                 │
                                 ▼
                    GitHub Actions  (.github/workflows/main.yml)
     ┌───────────────────────┬──────────────────────────┬─────────────────────────────┐
     │ job: test             │ job: docker              │ job: deploy                 │
     │ flake8 + pytest --cov │ login con PAT            │ SSH a la EC2 (llave .pem)   │
     │ cobertura >= 70 %     │ build :latest + :sha     │ docker pull :latest         │
     │                       │ push a Docker Hub ───────┼──► contenedor de prueba     │
     │                       │                          │    (8081) + health check    │
     │                       │                          │ quita el viejo, levanta el  │
     │                       │                          │ nuevo en 80 y lo verifica   │
     └───────────────────────┴──────────────────────────┴─────────────────────────────┘
                                                                    │
                                     Usuario ──HTTP :80──► EC2 Ubuntu + Docker
                                                           contenedor "api" (gunicorn :8000)
```

Si la imagen nueva no responde en `/api/health`, el pipeline falla **sin tocar** el contenedor que
está en producción. El paso final comprueba que `GET /api/health` responda con el hash del commit
recién publicado.

## Estructura del proyecto

```
SA/
├── .github/workflows/main.yml   # Pipeline CI/CD
├── data/
│   ├── seed.json                # Usuarios iniciales
│   └── store.py                 # "Base de datos" en memoria
├── routes/
│   ├── users.py                 # Endpoints de usuarios
│   ├── system.py                # GET /api/health
│   └── responses.py             # Formato estándar de respuesta
├── services/
│   ├── user_service.py          # Lógica de negocio de usuarios
│   └── validators.py            # Validación de cuerpos JSON
├── tests/                       # Pruebas pytest
├── scripts/setup_ec2.sh         # Instalación de Docker en la EC2
├── reporte/                     # Reporte en LaTeX
├── app.py                       # create_app()
├── config.py                    # VERSION y MESSAGE (se cambia en la demo)
├── Dockerfile
├── .dockerignore
├── requirements.txt / requirements-dev.txt
└── pytest.ini / .coveragerc / .flake8
```

## Endpoints (6)

Todas las respuestas tienen la forma `{"statusCode": 200, "data": ...}` o, en caso de error,
`{"statusCode": 4xx, "error": "mensaje"}`.

| # | Método | Ruta | Descripción | Códigos |
|---|--------|------|-------------|---------|
| 1 | GET | `/api/health` | Estado, versión, mensaje y commit desplegado | 200 |
| 2 | GET | `/api/users` | Listar usuarios | 200 |
| 3 | GET | `/api/users/{id}` | Consultar un usuario | 200, 404 |
| 4 | POST | `/api/users` | Crear usuario `{"name", "email", "role"?, "active"?}` | 201, 400, 409, 415 |
| 5 | PUT | `/api/users/{id}` | Actualizar uno o varios campos | 200, 400, 404, 409, 415 |
| 6 | DELETE | `/api/users/{id}` | Eliminar usuario | 200, 404 |

Reglas: `name` y `email` son obligatorios; el email debe tener formato válido, se guarda en
minúsculas y no puede repetirse (409); `role` solo acepta `admin` o `user`; no se permiten campos
extra como `id`.

> Los datos viven en memoria (se cargan de `data/seed.json`), por lo que se reinician en cada
> despliegue. Por eso gunicorn corre con 1 worker y 4 hilos: todas las peticiones comparten los
> mismos datos.

## Comandos locales

```powershell
# Entorno e instalación
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Levantar la API en modo desarrollo -> http://localhost:8000/api/health
python app.py

# Pruebas + cobertura (falla si la cobertura baja de 70 %)
pytest -v

# Lint
flake8 .

# Docker
docker build -t sa-cicd-api .
docker run -d --name api -p 8080:8000 sa-cicd-api
curl http://localhost:8080/api/health
docker rm -f api
```

## Configuración (una sola vez)

### 1. Docker Hub
1. Crear el repositorio público `sa-cicd-api` en https://hub.docker.com.
2. *Account settings → Personal access tokens → Generate new token* con permiso **Read & Write**.
   Guardar el token: se usa como secreto `DOCKERHUB_TOKEN`.

### 2. AWS EC2
1. Consola de AWS → EC2 → **Launch instance**: *Ubuntu Server 24.04 LTS*, tipo `t2.micro`/`t3.micro`.
2. Crear un **key pair** (formato `.pem`) y descargarlo. **Nunca** se sube al repositorio.
3. **Security Group** — reglas de entrada:

   | Tipo | Puerto | Origen |
   |------|--------|--------|
   | SSH  | 22 | `0.0.0.0/0` (GitHub Actions se conecta desde IPs variables) |
   | HTTP | 80 | `0.0.0.0/0` |

4. Conectarse e instalar Docker:

   ```bash
   ssh -i llave.pem ubuntu@<IP_EC2>
   curl -fsSL https://raw.githubusercontent.com/<usuario>/<repo>/main/scripts/setup_ec2.sh | sh
   # o copiar scripts/setup_ec2.sh con scp y ejecutar: sh setup_ec2.sh
   exit   # volver a entrar para que el grupo docker surta efecto
   ```

5. (Recomendado) Asignar una **Elastic IP** para que la IP pública no cambie al reiniciar la instancia.

### 3. GitHub Secrets
*Repositorio → Settings → Secrets and variables → Actions → New repository secret*:

| Secreto | Valor |
|---------|-------|
| `DOCKERHUB_USERNAME` | Usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Personal Access Token de Docker Hub |
| `EC2_HOST` | IP pública (o DNS) de la EC2 |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | Contenido completo del archivo `.pem` (incluyendo las líneas `BEGIN`/`END`) |

Ningún dato sensible (contraseñas, IPs, tokens, llaves) está en el código: todo se lee de
`secrets.*` en el workflow.

## Demostración en vivo

1. Abrir `http://<IP_EC2>/api/health` y mostrar el mensaje y el commit actuales.
2. Cambiar `MESSAGE` en `config.py`, por ejemplo:

   ```python
   MESSAGE = "Demo en vivo: versión 2"
   ```

3. `git commit -am "Cambia mensaje para demo" && git push`
4. En la pestaña **Actions** se ven los tres jobs: pruebas y cobertura → build/push a Docker Hub →
   despliegue en la EC2.
5. En Docker Hub aparece el tag nuevo con el hash del commit.
6. Recargar `http://<IP_EC2>/api/health`: muestra el mensaje nuevo y el nuevo `commit`.
