# 🚀 AI Interview API - Heroku Deployment Guide

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **Git**: Ensure your project is in a Git repository
3. **Heroku CLI**: Install the Heroku Command Line Interface

### Install Heroku CLI

**macOS:**
```bash
# Using Homebrew (recommended)
brew tap heroku/brew && brew install heroku

# Or download installer from:
# https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli
```

**Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

**Windows:**
Download the installer from [Heroku CLI page](https://devcenter.heroku.com/articles/heroku-cli)

## Quick Deployment (Automated)

Run the automated deployment script:

```bash
./deploy-heroku.sh
```

This script will:
- Check for Heroku CLI
- Login to Heroku
- Create your app
- Add PostgreSQL database
- Set environment variables
- Deploy your application

## Manual Deployment Steps

### 1. Login to Heroku

```bash
heroku login
```

### 2. Create Heroku Application

```bash
heroku create your-app-name
```

Replace `your-app-name` with a unique name for your application.

### 3. Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:mini
```

This creates a free PostgreSQL database and automatically sets the `DATABASE_URL` environment variable.

### 4. Set Environment Variables

```bash
# Required variables
heroku config:set SECRET_KEY="your-super-secret-key-minimum-32-characters"
heroku config:set OPENAI_API_KEY="sk-your-openai-api-key-here"
heroku config:set ADMIN_PASSWORD="your-secure-admin-password"

# Optional variables
heroku config:set ADMIN_EMAIL="admin@yourdomain.com"
heroku config:set DEBUG="false"
heroku config:set LOG_LEVEL="INFO"
```

### 5. Deploy to Heroku

```bash
git push heroku main
```

If your main branch is named differently (e.g., `master`):
```bash
git push heroku master
```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SECRET_KEY` | JWT signing key (32+ chars) | ✅ | `your-super-secret-key-here` |
| `OPENAI_API_KEY` | OpenAI API key for NLP | ✅ | `sk-...` |
| `ADMIN_PASSWORD` | Admin user password | ✅ | `SecureAdminPass123!` |
| `DATABASE_URL` | PostgreSQL connection URL | ✅ | Auto-set by Heroku |
| `ADMIN_EMAIL` | Admin user email | ❌ | `admin@yourdomain.com` |
| `DEBUG` | Enable debug mode | ❌ | `false` |
| `LOG_LEVEL` | Logging level | ❌ | `INFO` |

## Post-Deployment

### 1. Verify Deployment

```bash
# Check app status
heroku ps

# View logs
heroku logs --tail

# Open app in browser
heroku open
```

### 2. Test API Endpoints

```bash
# Health check
curl https://your-app-name.herokuapp.com/health

# API documentation
open https://your-app-name.herokuapp.com/docs
```

### 3. Database Migration (if needed)

If you have database migrations:
```bash
heroku run python -m alembic upgrade head
```

## Useful Heroku Commands

```bash
# View app information
heroku info

# View environment variables
heroku config

# View database information
heroku pg:info

# Create database backup
heroku pg:backups:capture

# Scale dynos
heroku ps:scale web=1

# Restart application
heroku restart

# Run one-off commands
heroku run python -c "print('Hello from Heroku!')"
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check `requirements.txt` for correct dependencies
   - Ensure Python version compatibility
   - View build logs: `heroku logs --tail`

2. **Database Connection Errors**
   - Verify `DATABASE_URL` is set: `heroku config:get DATABASE_URL`
   - Check PostgreSQL addon status: `heroku addons`

3. **Environment Variable Issues**
   - List all variables: `heroku config`
   - Update variables: `heroku config:set VAR_NAME="value"`

4. **Application Crashes**
   - Check logs: `heroku logs --tail`
   - Verify Procfile configuration
   - Check dyno status: `heroku ps`

### Logs and Debugging

```bash
# View recent logs
heroku logs

# Stream live logs
heroku logs --tail

# View logs for specific dyno
heroku logs --dyno web.1

# View logs with timestamps
heroku logs --tail --timestamp
```

## Scaling and Performance

### Free Tier Limitations
- 550-1000 free dyno hours per month
- Apps sleep after 30 minutes of inactivity
- 10,000 rows in PostgreSQL database

### Upgrading
```bash
# Upgrade to hobby dyno ($7/month)
heroku ps:scale web=1:hobby

# Upgrade database to hobby-basic ($9/month)
heroku addons:upgrade heroku-postgresql:hobby-basic
```

## Security Best Practices

- ✅ Use strong `SECRET_KEY` (32+ characters)
- ✅ Set `DEBUG=false` in production
- ✅ Use secure `ADMIN_PASSWORD`
- ✅ Regularly rotate API keys
- ✅ Monitor application logs
- ✅ Keep dependencies updated

## Support

- 📖 Heroku Documentation: https://devcenter.heroku.com/
- 🆘 Heroku Support: https://help.heroku.com/
- 📚 API Documentation: https://your-app-name.herokuapp.com/docs
