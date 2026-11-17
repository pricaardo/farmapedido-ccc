# FarmaPedido CCC

## Desenvolvimento local

Backend:

```powershell
python manage.py migrate
python manage.py runserver
```

Frontend, em outro terminal:

```powershell
cd frontend
npm install
npm run dev
```

Abra http://localhost:5173/. Sem variáveis de ambiente, o backend usa SQLite e configurações de desenvolvimento.

## Deploy no Render

O backend e o frontend são serviços separados. Crie um banco PostgreSQL no Render e use a **Internal Database URL** como `DATABASE_URL` do serviço backend.

### Serviço Web (backend)

- Runtime: Python
- Build command: `pip install -r requirements.txt && python manage.py collectstatic --no-input`
- Start command: `python manage.py migrate --noinput && gunicorn backend.wsgi:application`

Configure estas variáveis no serviço:

| Variável | Valor |
| --- | --- |
| `DEBUG` | `False` |
| `SECRET_KEY` | Gere um valor secreto no Render; não use a chave local |
| `ALLOWED_HOSTS` | Host do serviço backend, por exemplo `farmapedido-api.onrender.com` |
| `DATABASE_URL` | Internal Database URL do PostgreSQL |
| `CORS_ALLOWED_ORIGINS` | URL HTTPS do serviço frontend |
| `CSRF_TRUSTED_ORIGINS` | URL HTTPS do serviço frontend |

O Render fornece `RENDER_EXTERNAL_HOSTNAME`; a configuração o inclui automaticamente em `ALLOWED_HOSTS`.

### Static Site (frontend)

- Root directory: vazio (raiz do repositório)
- Build command: `cd frontend && npm ci && npm run build`
- Publish directory: `frontend/dist`

Configure `VITE_API_BASE_URL` com a URL do backend terminada em `/api`, por exemplo:

```text
https://farmapedido-api.onrender.com/api
```

Depois de alterar os domínios dos serviços, atualize também `CORS_ALLOWED_ORIGINS` e `CSRF_TRUSTED_ORIGINS` no backend e faça novo deploy do frontend.
