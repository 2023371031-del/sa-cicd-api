# SA — Pipeline CI/CD para API REST (Flask + Docker + GitHub Actions + AWS EC2)

API REST en **Python/Flask** con **75 endpoints**, **181 pruebas** con **pytest** (cobertura del 99 %,
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
está en producción. El paso final comprueba que `GET /api/version` responda con el hash del commit
recién publicado.

## Estructura del proyecto

```
SA/
├── .github/workflows/main.yml   # Pipeline CI/CD
├── data/
│   ├── seed.json                # Datos iniciales
│   └── store.py                 # "Base de datos" en memoria
├── routes/                      # Un archivo de rutas por recurso (Blueprints)
│   ├── crud.py                  # Fábrica de los 6 endpoints CRUD
│   ├── responses.py             # Formato estándar de respuesta
│   ├── users.py, products.py, categories.py, suppliers.py, customers.py,
│   ├── orders.py, departments.py, employees.py, reviews.py, coupons.py
│   └── system.py                # health, version, endpoints, stats, reset
├── services/
│   ├── crud_service.py          # Lógica de negocio (unicidad, llaves foráneas, etc.)
│   ├── schemas.py               # Esquema de campos de cada recurso
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

## Endpoints (75)

Todas las respuestas tienen la forma `{"statusCode": 200, "data": ...}` o, en caso de error,
`{"statusCode": 4xx, "error": "mensaje"}`.

### CRUD — 6 endpoints × 10 recursos = 60

Recursos: `users`, `categories`, `suppliers`, `products`, `customers`, `orders`, `departments`,
`employees`, `reviews`, `coupons`.

| Método | Ruta | Descripción | Códigos |
|--------|------|-------------|---------|
| GET | `/api/<recurso>` | Listar. Admite `?campo=valor`, `?q=texto`, `?sort=campo` / `?sort=-campo`, `?limit=`, `?offset=` | 200, 400 |
| GET | `/api/<recurso>/{id}` | Consultar uno | 200, 404 |
| POST | `/api/<recurso>` | Crear | 201, 400, 409, 415 |
| PUT | `/api/<recurso>/{id}` | Reemplazar (todos los campos obligatorios) | 200, 400, 404, 409, 415 |
| PATCH | `/api/<recurso>/{id}` | Actualizar parcialmente | 200, 400, 404, 409, 415 |
| DELETE | `/api/<recurso>/{id}` | Eliminar (409 si otro registro lo referencia) | 200, 404, 409 |

### Endpoints adicionales — 15

| # | Método | Ruta | Descripción |
|---|--------|------|-------------|
| 61 | GET | `/api/health` | Estado del servicio y tiempo activo |
| 62 | GET | `/api/version` | Versión, mensaje y commit desplegado |
| 63 | GET | `/api/endpoints` | Lista todos los endpoints registrados |
| 64 | GET | `/api/stats` | Número de registros por tabla |
| 65 | POST | `/api/admin/reset` | Reinicia los datos iniciales |
| 66 | GET | `/api/categories/{id}/products` | Productos de una categoría |
| 67 | GET | `/api/suppliers/{id}/products` | Productos de un proveedor |
| 68 | GET | `/api/products/low-stock?threshold=10` | Productos con poco inventario |
| 69 | GET | `/api/products/{id}/reviews` | Reseñas de un producto |
| 70 | GET | `/api/products/{id}/rating` | Calificación promedio de un producto |
| 71 | GET | `/api/customers/{id}/orders` | Pedidos de un cliente |
| 72 | POST | `/api/orders/{id}/cancel` | Cancela un pedido (409 si ya se envió o canceló) |
| 73 | GET | `/api/departments/{id}/employees` | Empleados de un departamento |
| 74 | POST | `/api/users/{id}/toggle-active` | Activa/desactiva un usuario |
| 75 | POST | `/api/coupons/validate` | Valida un código de cupón (`{"code": "..."}`) |

Reglas de negocio destacadas: el email y otros campos `unique` no se repiten (409); las llaves
foráneas (`category_id`, `customer_id`, …) deben existir (400); el `total` de un pedido lo calcula
el servidor (`precio × cantidad`); los códigos de cupón se guardan en mayúsculas.

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

1. Abrir `http://<IP_EC2>/api/version` y mostrar el mensaje y el commit actuales.
2. Cambiar `MESSAGE` en `config.py`, por ejemplo:

   ```python
   MESSAGE = "Demo en vivo: versión 2"
   ```

3. `git commit -am "Cambia mensaje para demo" && git push`
4. En la pestaña **Actions** se ven los tres jobs: pruebas y cobertura → build/push a Docker Hub →
   despliegue en la EC2.
5. En Docker Hub aparece el tag nuevo con el hash del commit.
6. Recargar `http://<IP_EC2>/api/version`: muestra el mensaje nuevo y el nuevo `commit`.
