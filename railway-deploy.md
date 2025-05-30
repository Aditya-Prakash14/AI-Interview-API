# 🚀 Deploy AI Interview API to Railway

## Quick Deploy Steps

### 1. Prepare Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Deploy to Railway

#### Option A: One-Click Deploy (Recommended)
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository
5. Railway will auto-detect the Dockerfile and deploy

#### Option B: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Add PostgreSQL database
railway add postgresql

# Deploy
railway up
```

### 3. Set Environment Variables

In Railway dashboard, go to your project → Variables and set:

**Required Variables:**
```
SECRET_KEY=your-super-secret-key-minimum-32-characters-long
OPENAI_API_KEY=sk-your-openai-api-key-here
ADMIN_PASSWORD=your-secure-admin-password
DEBUG=false
```

**Optional Variables:**
```
ADMIN_EMAIL=admin@yourdomain.com
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_FILE_SIZE_MB=50
```

**Note:** `DATABASE_URL` is automatically set when you add PostgreSQL

### 4. Custom Domain (Optional)
1. In Railway dashboard, go to Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

### 5. Test Deployment
```bash
# Health check
curl https://your-app.railway.app/health

# API documentation
curl https://your-app.railway.app/docs
```

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | ✅ | JWT signing key (32+ chars) | `your-super-secret-key-here` |
| `OPENAI_API_KEY` | ✅ | OpenAI API key | `sk-...` |
| `ADMIN_PASSWORD` | ✅ | Admin user password | `SecurePass123!` |
| `DATABASE_URL` | ✅ | PostgreSQL URL (auto-set) | `postgresql://...` |
| `DEBUG` | ❌ | Debug mode (default: true) | `false` |
| `ADMIN_EMAIL` | ❌ | Admin email | `admin@yourdomain.com` |
| `PORT` | ❌ | Port (auto-set by Railway) | `8000` |

## Post-Deployment

### 1. Verify Health
```bash
curl https://your-app.railway.app/health
```

### 2. Test Admin Login
```bash
curl -X POST https://your-app.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-admin-password"}'
```

### 3. Load Sample Data
Use the admin panel or API to upload sample questions.

## Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check Dockerfile syntax
   - Verify requirements.txt dependencies
   - Check Railway build logs

2. **Database Connection Error**
   - Ensure PostgreSQL service is added
   - Check DATABASE_URL is set correctly
   - Verify database is running

3. **OpenAI API Errors**
   - Verify OPENAI_API_KEY is correct
   - Check API quota and billing
   - Ensure key has required permissions

### View Logs:
```bash
railway logs
```

## Production Checklist

- ✅ Strong SECRET_KEY (32+ characters)
- ✅ Secure ADMIN_PASSWORD
- ✅ DEBUG=false
- ✅ HTTPS enabled (automatic on Railway)
- ✅ PostgreSQL database connected
- ✅ Environment variables secured
- ✅ Custom domain configured (optional)

## Scaling

Railway automatically handles:
- Load balancing
- Auto-scaling based on traffic
- Database backups
- SSL certificates
- CDN for static assets

## Monitoring

- **Health Check**: `/health`
- **Logs**: Railway dashboard
- **Metrics**: Railway dashboard
- **Uptime**: Railway provides 99.9% uptime SLA

Your AI Interview API will be live at: `https://your-app.railway.app`
