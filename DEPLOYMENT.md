# 🚀 AI Interview API - Production Deployment Guide

## Quick Deploy to Railway (Recommended)

### Option 1: One-Click Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### Option 2: Manual Railway Deployment

1. **Fork this repository** to your GitHub account

2. **Create Railway account** at [railway.app](https://railway.app)

3. **Create new project** from GitHub repository:
   - Connect your GitHub account
   - Select the forked repository
   - Railway will auto-detect the Dockerfile

4. **Add PostgreSQL database**:
   - In Railway dashboard, click "Add Service"
   - Select "PostgreSQL"
   - Railway will automatically set `DATABASE_URL`

5. **Set environment variables** in Railway dashboard:
   ```
   SECRET_KEY=your-super-secret-key-minimum-32-characters
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ADMIN_EMAIL=admin@yourdomain.com
   ADMIN_PASSWORD=your-secure-admin-password
   DEBUG=false
   LOG_LEVEL=INFO
   ```

6. **Deploy**: Railway will automatically build and deploy your application

7. **Get your URL**: Railway provides a public URL like `https://your-app.railway.app`

## Alternative Deployment Options

### Deploy to Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   heroku config:set OPENAI_API_KEY="your-openai-key"
   heroku config:set ADMIN_PASSWORD="your-admin-password"
   heroku config:set DEBUG="false"
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

### Deploy to DigitalOcean App Platform

1. **Create account** at [DigitalOcean](https://digitalocean.com)

2. **Create new app** from GitHub repository

3. **Configure app**:
   - Runtime: Python
   - Build command: `pip install -r requirements-prod.txt`
   - Run command: `uvicorn app.main_prod:app --host 0.0.0.0 --port 8080`

4. **Add PostgreSQL database** from DigitalOcean marketplace

5. **Set environment variables** in app settings

### Deploy with Docker

1. **Build image**:
   ```bash
   docker build -t ai-interview-api .
   ```

2. **Run container**:
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e SECRET_KEY="your-secret-key" \
     -e OPENAI_API_KEY="your-openai-key" \
     -e ADMIN_PASSWORD="your-admin-password" \
     -e DATABASE_URL="postgresql://..." \
     ai-interview-api
   ```

## Required Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SECRET_KEY` | JWT signing key (32+ chars) | ✅ | `your-super-secret-key-here` |
| `OPENAI_API_KEY` | OpenAI API key for NLP | ✅ | `sk-...` |
| `ADMIN_PASSWORD` | Admin user password | ✅ | `SecureAdminPass123!` |
| `DATABASE_URL` | PostgreSQL connection URL | ✅ | `postgresql://user:pass@host/db` |
| `ADMIN_EMAIL` | Admin user email | ❌ | `admin@yourdomain.com` |
| `DEBUG` | Enable debug mode | ❌ | `false` |
| `LOG_LEVEL` | Logging level | ❌ | `INFO` |
| `MAX_FILE_SIZE_MB` | Max audio file size | ❌ | `50` |
| `RATE_LIMIT_REQUESTS` | Rate limit per hour | ❌ | `100` |

## Post-Deployment Setup

### 1. Test the Deployment
```bash
# Health check
curl https://your-app.railway.app/health

# API info
curl https://your-app.railway.app/
```

### 2. Create Admin User
The admin user is automatically created on startup using the `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables.

### 3. Test Authentication
```bash
# Login as admin
curl -X POST https://your-app.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-admin-password"}'
```

### 4. Load Sample Questions
Use the admin panel or API to upload the sample questions from `sample_questions.csv`.

## Security Checklist

- ✅ Strong `SECRET_KEY` (32+ characters)
- ✅ Secure `ADMIN_PASSWORD`
- ✅ `DEBUG=false` in production
- ✅ HTTPS enabled (automatic on Railway/Heroku)
- ✅ Rate limiting enabled
- ✅ CORS configured for your domain
- ✅ Database connection encrypted
- ✅ Environment variables secured

## Monitoring and Maintenance

### Health Monitoring
- Health endpoint: `/health`
- Metrics endpoint: `/metrics` (debug mode only)
- Logs available in platform dashboard

### Database Backups
- Railway: Automatic backups
- Heroku: `heroku pg:backups:capture`
- DigitalOcean: Automatic backups available

### Scaling
- Railway: Auto-scaling available
- Heroku: `heroku ps:scale web=2`
- DigitalOcean: Horizontal scaling in dashboard

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check `DATABASE_URL` format
   - Ensure database is running
   - Verify network connectivity

2. **OpenAI API Errors**
   - Verify `OPENAI_API_KEY` is correct
   - Check API quota and billing
   - Ensure key has required permissions

3. **File Upload Issues**
   - Check `MAX_FILE_SIZE_MB` setting
   - Verify disk space availability
   - Ensure upload directory permissions

### Logs
```bash
# Railway
railway logs

# Heroku
heroku logs --tail

# Docker
docker logs container-name
```

## Support

- 📧 Email: support@yourdomain.com
- 📖 Documentation: https://your-app.railway.app/docs
- 🐛 Issues: GitHub Issues
- 💬 Discord: Your Discord Server

## License

This project is licensed under the MIT License - see the LICENSE file for details.
