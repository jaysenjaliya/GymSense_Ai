# Deployment Guide

Production targets:
- **Backend** → AWS EC2 free tier, Dockerized, behind **Nginx** + **Let's Encrypt** TLS, on a **DuckDNS** hostname.
- **Database** → **MongoDB Atlas** (free M0 cluster).
- **Frontend** → **Vercel**.

```
Browser ──HTTPS──▶ Nginx (EC2 :443) ──▶ backend container (127.0.0.1:8000) ──▶ MongoDB Atlas
   │
   └──────────────▶ Vercel (frontend static site) ──API calls──▶ https://<subdomain>.duckdns.org
```

---

## 1. MongoDB Atlas
1. Create a free **M0** cluster at https://cloud.mongodb.com.
2. Add a database user and allow your EC2 IP (or `0.0.0.0/0` for testing) in Network Access.
3. Copy the connection string → this becomes `MONGO_URI` in `backend/.env`.

## 2. DuckDNS (dynamic DNS)
1. Create a subdomain at https://duckdns.org and point it at your EC2 public IP.
2. Add the DuckDNS updater cron on the instance so the IP stays current:
   ```bash
   # every 5 min
   */5 * * * * curl -s "https://www.duckdns.org/update?domains=<SUB>&token=<TOKEN>&ip="
   ```
3. Put `<SUB>.duckdns.org` in `server_name` in `infra/nginx/nginx.conf`.

## 3. EC2 instance
1. Launch an Ubuntu t2.micro (free tier). Security group: open **22, 80, 443**.
2. Install Docker + Compose:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-plugin nginx
   sudo usermod -aG docker $USER && newgrp docker
   ```
3. Clone the repo and create `backend/.env` (copy `backend/.env.example`, fill in
   `MONGO_URI` (Atlas), `JWT_SECRET_KEY`, `LLM_API_KEY`). **Also copy the model
   file** to `backend/app/models/model_weights.pt` (it's gitignored — transfer via
   `scp`).
4. Start the backend:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   curl -s localhost:8000/health   # {"status":"ok"}
   ```

## 4. Nginx + TLS
1. Install the site config:
   ```bash
   sudo cp infra/nginx/nginx.conf /etc/nginx/sites-available/gymsense
   sudo ln -s /etc/nginx/sites-available/gymsense /etc/nginx/sites-enabled/
   sudo rm -f /etc/nginx/sites-enabled/default
   sudo nginx -t && sudo systemctl reload nginx
   ```
2. Issue the certificate (edits Nginx to add the 443 block + auto-renew):
   ```bash
   sudo apt install -y certbot python3-certbot-nginx
   sudo certbot --nginx -d <SUB>.duckdns.org
   ```
   Note: `client_max_body_size 25m` is already set so CSV uploads aren't rejected.

## 5. Frontend on Vercel
1. Import the repo in Vercel; set **Root Directory** = `frontend`.
2. Vercel auto-detects Vite (`vercel.json` pins build/output + SPA rewrites).
3. Set env var **`VITE_API_BASE_URL`** = `https://<SUB>.duckdns.org`.
4. Add that Vercel domain to the backend's `CORS_ORIGINS` in `backend/.env`, then
   `docker compose -f docker-compose.prod.yml up -d` to reload.

## 6. Updating a deployment
```bash
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## Notes
- Free-tier RAM is tight (1 GB) and PyTorch loads per worker — keep
  `WEB_CONCURRENCY=1`. Scale up the instance before adding workers.
- Rotate `JWT_SECRET_KEY` / `LLM_API_KEY` if they were ever shared in plaintext.
- CI (`.github/workflows/ci.yml`) runs backend tests, frontend build, and a Docker
  build on every push/PR.
