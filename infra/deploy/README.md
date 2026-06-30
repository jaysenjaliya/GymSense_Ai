# Deployment Notes

Production targets: **backend on AWS EC2 free tier** (Dockerized, behind Nginx +
Let's Encrypt SSL via a DuckDNS hostname) and **frontend on Vercel**.

## Backend — EC2
1. Launch an EC2 free-tier instance (Ubuntu); open ports 22, 80, 443.
2. Install Docker + Docker Compose and Nginx (or run Nginx in a container).
3. Clone the repo, create `backend/.env` from `.env.example`.
4. `docker compose up -d --build` (backend + mongo, or use MongoDB Atlas instead
   of the local mongo container in production).

## DNS — DuckDNS
1. Create a subdomain at https://duckdns.org and point it at the EC2 public IP.
2. Add a cron job / systemd timer to refresh the DuckDNS IP on a schedule.
3. Set `server_name` in `infra/nginx/nginx.conf` to `<subdomain>.duckdns.org`.

## SSL — Let's Encrypt
1. `sudo certbot --nginx -d <subdomain>.duckdns.org`
2. Certbot edits the Nginx config to add the 443 server block and auto-renews.

## Frontend — Vercel
1. Import the repo in Vercel; set **Root Directory** = `frontend`.
2. Build command `npm run build`, output dir `dist`.
3. Set env var `VITE_API_BASE_URL` to the HTTPS DuckDNS backend URL.

## TODO
- Pin image tags / versions for reproducible deploys.
- Add a GitHub Actions deploy step (SSH to EC2, pull, recompose).
