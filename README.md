# Streeling University Library – Inventory Management System

## Requirements

- Python 3.8+
- Node.js v18+
- Docker and Docker Compose

---

## Backend Setup

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Create a `.env` file in the project root:
```
DATABASE_PATH=library.db
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
FLASK_ENV=development
FLASK_DEBUG=True
```

3. Initialise the database:
```bash
python3 init_db.py
```

4. Start the backend:
```bash
python3 app.py
```

Backend runs at `http://localhost:5000`

---

## Frontend Setup

1. Navigate to the frontend folder:
```bash
cd ims-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the frontend:
```bash
npm start
```

Frontend runs at `http://localhost:3000` and connects to the backend at `http://localhost:5000/api`

---

## CI/CD Pipeline Setup

1. Ensure Docker and Docker Compose are installed.

2. From the project root, build and start all services:
```bash
docker compose up -d --build
```

This starts four containers:
- `ccse-jenkins` — Jenkins on http://localhost:8080
- `ccse-sonarqube` — SonarQube on http://localhost:9000
- `ccse-sonar-db` — PostgreSQL (SonarQube backend)
- `ccse-zap` — OWASP ZAP on http://localhost:8090

3. Retrieve the Jenkins initial admin password:
```bash
docker exec -it ccse-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

4. Open Jenkins at `http://localhost:8080`, paste the password and complete setup.

5. In Jenkins, add the following credentials under **Manage Jenkins → Credentials**:
   - `gitlab-pat` — Username with password (GitLab Personal Access Token)
   - `sonar-token` — Secret text (SonarQube User Token)

6. In Jenkins, configure SonarQube under **Manage Jenkins → System → SonarQube servers**:
   - Name: `SonarQube`
   - URL: `http://ccse-sonarqube:9000`
   - Token: `sonar-token`

7. In Jenkins, configure SonarScanner under **Manage Jenkins → Tools → SonarQube Scanner**:
   - Name: `SonarScanner`
   - Enable: Install automatically

8. Create a new Pipeline job pointing to this repository with branch `*/main` and script path `Jenkinsfile`.

9. Click **Build Now** to run the pipeline.

---

## Default Test Users

| Role | Username | Password |
|------|----------|----------|
| Librarian | librarian | admin123 |
| Student | student | student123 |

---

## API Endpoints

**Authentication**
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/profile`

**Inventory** (authentication required)
- `GET /api/inventory/books`
- `POST /api/inventory/books` (librarian only)
- `PUT /api/inventory/books/<id>` (librarian only)
- `DELETE /api/inventory/books/<id>` (librarian only)
- `GET /api/inventory/books/<id>`
- `GET /api/inventory/categories`

**Audit Logs** (librarian only)
- `GET /api/audit/logs`
- `GET /api/audit/logs/summary`
- `GET /api/audit/logs/export`