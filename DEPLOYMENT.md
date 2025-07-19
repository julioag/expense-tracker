# Deployment Guide - Render

This guide walks you through deploying the Expense Tracker API on Render.

## Prerequisites

1. A [Render](https://render.com) account
2. Your expense tracker code in a Git repository (GitHub, GitLab, etc.)

## Step-by-Step Deployment

### 1. Create a PostgreSQL Database

1. **Log into Render Dashboard**
2. **Click "New +"** → **"PostgreSQL"**
3. **Configure Database:**
   - Name: `expense-tracker-db`
   - Database Name: `expense_tracker`
   - User: `expense_user`
   - Region: Choose closest to your location
   - Plan: **Free** (for development)

4. **Click "Create Database"**
5. **Save the Connection Details** - you'll need the "Internal Database URL"

### 2. Deploy the Web Service

1. **Click "New +"** → **"Web Service"**
2. **Connect Repository:**
   - Choose your Git provider
   - Select your expense-tracker repository
   - Choose the main/master branch

3. **Configure Service:**
   ```
   Name: expense-tracker-api
   Region: Same as your database
   Branch: main (or master)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python start.py
   Plan: Free
   ```

4. **Environment Variables:**
   Click "Advanced" and add these environment variables:
   ```
   DATABASE_URL: [Paste your PostgreSQL Internal Database URL]
   ENVIRONMENT: production
   PORT: 10000
   ```

5. **Click "Create Web Service"**

### 3. Verify Deployment

1. **Wait for Build** - This takes 5-10 minutes for the first deployment
2. **Check Logs** - Look for:
   ```
   🚀 Starting Expense Tracker API...
   📦 Initializing database...
   ✅ Database initialized successfully!
   🌐 Starting FastAPI server...
   ```

3. **Test the API:**
   - Your service URL will be: `https://expense-tracker-api.onrender.com`
   - Visit: `https://your-service-url.onrender.com/docs`
   - You should see the FastAPI documentation

### 4. Test the Deployment

```bash
# Health check
curl https://your-service-url.onrender.com/health

# Get categories (should show the default 9 categories)
curl https://your-service-url.onrender.com/categories/

# Create a test expense
curl -X POST "https://your-service-url.onrender.com/expenses/" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 10.99,
    "merchant": "Test Merchant",
    "description": "Test expense",
    "transaction_date": "2024-01-15T10:30:00"
  }'
```

## Important Notes

### Database Connection
- Render provides the database URL automatically
- The connection string format is handled in `app/database.py`
- Database tables are created automatically on first startup

### Free Tier Limitations
- **Web Service**: Sleeps after 15 minutes of inactivity
- **Database**: 1GB storage, expires after 90 days
- **Cold starts**: First request after sleeping takes ~30 seconds

### Custom Domain (Optional)
1. Go to your web service settings
2. Click "Custom Domains"
3. Add your domain and configure DNS

### Monitoring
- **Logs**: Available in Render dashboard
- **Metrics**: Basic metrics available
- **Health Check**: Use `/health` endpoint

## Troubleshooting

### Common Issues

**Build Fails:**
- Check that `requirements.txt` is in the root directory
- Verify all dependencies are listed

**Database Connection Error:**
- Ensure `DATABASE_URL` environment variable is set correctly
- Check that database and web service are in the same region

**Service Won't Start:**
- Check the start command: `python start.py`
- Review logs for specific error messages

**Import Errors:**
- Ensure all Python files are in the correct directory structure
- Check that `__init__.py` files exist in all package directories

### Getting Help

1. **Check Render Logs** - Most issues are visible in the deployment logs
2. **Render Documentation** - https://render.com/docs
3. **Community Support** - Render Discord/Community forums

## Next Steps

After successful deployment:

1. **Set up n8n Integration** (Iteration 2)
   - Use your Render URL for webhook endpoints
   - Example webhook: `https://your-service-url.onrender.com/expenses/webhook`

2. **Implement MCP for LM Studio** (Iteration 3)
   - Analytics endpoints are ready
   - Use Render URL for MCP server configuration

3. **Production Considerations**
   - Upgrade to paid plans for production use
   - Set up monitoring and alerts
   - Configure proper CORS settings
   - Add authentication/authorization 