# OAuth greeting API

A small Django authentication exercise: sign in with a Django user account, receive a one-hour bearer token, then submit a greeting to a protected endpoint. The repository name reflects its original learning context; this is not a learning-management platform.

## Follow one request

```mermaid
sequenceDiagram
  participant Client
  participant Django
  participant TokenStore
  Client->>Django: POST /signin with JSON credentials
  Django->>Django: authenticate() checks password hash and active status
  Django->>TokenStore: Create expiring access token
  Django-->>Client: access_token
  Client->>Django: POST /greeting with Bearer token
  Django-->>Client: message
```

## Local setup

`requirements-core.txt` contains the dependencies this API imports. The original broad environment export remains in `requirements.txt` for historical context; the API does not need its unrelated ML and Tutor packages.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-core.txt
export DJANGO_SECRET_KEY="choose-a-private-local-signing-key"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Provide a persistent private signing key in the environment; the fallback is a temporary development key. The SQLite database is created locally. Create a normal Django user through the admin or shell to try the flow.

```bash
curl -X POST http://127.0.0.1:8000/signin \
  -H 'Content-Type: application/json' \
  -d '{"username":"demo","password":"your-local-password"}'

curl -X POST http://127.0.0.1:8000/greeting \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_LOCAL_ACCESS_TOKEN' \
  -d '{"greeting":"Hello"}'
```

A valid greeting of `Hello` returns `{"message":"Goodbye!"}`. Other nonempty strings return `Greeting received!`. Sign-in accepts nonempty string credentials; malformed JSON and invalid credentials return 400. A stored password hash cannot be used as the password, and inactive users cannot sign in.

## Verify the authentication boundary

```bash
python manage.py test core
```

Regression tests cover real hashed passwords, rejected hash-as-password attempts, inactive accounts, malformed input, and authenticated/unauthenticated greeting requests.

This custom sign-in flow is a learning exercise, not a complete OAuth authorization server integration. It uses the first configured OAuth application when present and permits a nullable application for the local demo. Before shared deployment, require an explicitly configured client, adopt a standard authorization flow, add sign-in throttling, configure HTTPS/hosts, disable debug mode, and define token revocation. No production credentials are included.
