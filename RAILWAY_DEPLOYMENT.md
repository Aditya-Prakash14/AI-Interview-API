# 🚀 AI Interview API - Railway Deployment Guide

## ✅ Repository Status: LIVE ON GITHUB
**Repository URL**: https://github.com/Aditya-Prakash14/AI-Interview-API

## 🚂 Deploy to Railway (Step-by-Step)

### **Option 1: One-Click Deploy (Recommended)**

1. **Go to Railway**: https://railway.app
2. **Sign up/Login** with your GitHub account
3. **Click "Start a New Project"**
4. **Select "Deploy from GitHub repo"**
5. **Choose**: `Aditya-Prakash14/AI-Interview-API`
6. **Railway will auto-detect** the configuration and start building

### **Option 2: Direct Deploy Button**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/your-template-id)

### **Step 3: Add PostgreSQL Database**

1. In your Railway project dashboard
2. Click **"+ New Service"**
3. Select **"Database"** → **"PostgreSQL"**
4. Railway will automatically set the `DATABASE_URL` environment variable

### **Step 4: Configure Environment Variables**

In Railway dashboard → **Variables** tab, add these:

```bash
# REQUIRED VARIABLES
SECRET_KEY=your-super-secret-key-minimum-32-characters-long-change-this
OPENAI_API_KEY=sk-your-openai-api-key-here-get-from-openai-platform
ADMIN_PASSWORD=your-secure-admin-password-change-this
DEBUG=false

# OPTIONAL VARIABLES
ADMIN_EMAIL=admin@yourdomain.com
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_FILE_SIZE_MB=50
ALLOWED_AUDIO_FORMATS=mp3,wav,m4a,flac
```

### **Step 5: Generate Strong Keys**

**For SECRET_KEY**, use one of these methods:
```bash
# Method 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 2: OpenSSL
openssl rand -base64 32

# Method 3: Online generator
# Visit: https://generate-secret.vercel.app/32
```

**For ADMIN_PASSWORD**, create a strong password:
- Minimum 12 characters
- Include uppercase, lowercase, numbers, symbols
- Example: `AdminPass123!@#`

### **Step 6: Deploy and Monitor**

1. **Save environment variables**
2. **Railway will automatically redeploy**
3. **Monitor the build logs** in Railway dashboard
4. **Wait for deployment to complete** (usually 2-5 minutes)

### **Step 7: Get Your Live URL**

1. In Railway dashboard → **Settings** → **Domains**
2. Your app will be available at: `https://your-app-name.railway.app`
3. **Copy this URL** - this is your production API!

## 🧪 Test Your Deployment

### **1. Health Check**
```bash
curl https://your-app-name.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **2. API Documentation**
Visit: `https://your-app-name.railway.app/docs`

### **3. Test Admin Login**
```bash
curl -X POST https://your-app-name.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-admin-password"
  }'
```

### **4. Test User Registration**
```bash
curl -X POST https://your-app-name.railway.app/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

## 🔧 Post-Deployment Setup

### **1. Load Sample Questions**

1. **Login as admin** at: `https://your-app-name.railway.app/docs`
2. **Use the admin endpoints** to create questions
3. **Or upload the sample CSV** using the bulk import endpoint

### **2. Configure Custom Domain (Optional)**

1. In Railway dashboard → **Settings** → **Domains**
2. **Add custom domain**: `api.yourdomain.com`
3. **Update DNS records** as instructed by Railway
4. **SSL certificate** will be automatically provisioned

### **3. Monitor Your Application**

- **Logs**: Railway dashboard → **Deployments** → **View Logs**
- **Metrics**: Railway dashboard → **Metrics**
- **Health**: `https://your-app-name.railway.app/health`

## 🚨 Troubleshooting

### **Common Issues:**

1. **Build Fails**
   - Check Railway build logs
   - Verify `requirements.txt` is correct
   - Ensure all files are committed to GitHub

2. **Database Connection Error**
   - Verify PostgreSQL service is added
   - Check `DATABASE_URL` is automatically set
   - Restart the application service

3. **Environment Variables Not Set**
   - Go to Railway dashboard → Variables
   - Ensure all required variables are set
   - Redeploy after adding variables

4. **OpenAI API Errors**
   - Verify `OPENAI_API_KEY` is correct
   - Check OpenAI account has credits
   - Ensure API key has required permissions

### **View Logs:**
```bash
# In Railway dashboard
Deployments → Latest Deployment → View Logs
```

## ✅ Deployment Checklist

- ✅ Repository pushed to GitHub
- ✅ Railway project created
- ✅ PostgreSQL database added
- ✅ Environment variables configured
- ✅ Application deployed successfully
- ✅ Health check passing
- ✅ API documentation accessible
- ✅ Admin login working
- ✅ Sample data loaded (optional)
- ✅ Custom domain configured (optional)

## 🎉 Success!

Your AI Interview API is now **LIVE IN PRODUCTION**!

**🌐 Access Points:**
- **API Base**: `https://your-app-name.railway.app`
- **Documentation**: `https://your-app-name.railway.app/docs`
- **Health Check**: `https://your-app-name.railway.app/health`

**🔐 Admin Access:**
- **Username**: `admin`
- **Password**: `[Your ADMIN_PASSWORD]`

**🚀 Start conducting AI-powered interviews today!**

## 📞 Support

If you encounter any issues:
1. Check Railway build logs
2. Verify environment variables
3. Test API endpoints
4. Review this deployment guide

**Happy interviewing! 🎯**
