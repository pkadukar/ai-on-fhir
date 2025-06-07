
```makefile
.PHONY: backend frontend login setup docker-backend

# Run Flask backend
backend:
	cd backend && venv/bin/python app.py

# Run frontend (Vite/Next.js dev server)
frontend:
	cd frontend && npm run dev

# Backend setup (only once)
setup:
	cd backend && python3 -m venv venv && venv/bin/pip install -r requirements.txt && venv/bin/python -m spacy download en_core_web_sm

# Sample curl to login and get token
login:
	curl -X POST http://localhost:5050/login \
	 -H "Content-Type: application/json" \
	 -d '{"username": "testuser", "password": "testpass"}'

# Docker: Build and run backend container
docker-backend:
	docker build -t ai-on-fhir-backend ./backend
	docker run -p 5050:5050 --rm ai-on-fhir-backend
