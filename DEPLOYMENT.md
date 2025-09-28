# 🚀 Deployment Guide

This guide covers deploying the Amazon Review Intelligence Suite to various platforms.

## 📋 Prerequisites

- GitHub repository with your code
- Backend API deployed and accessible
- Domain name (optional but recommended)

## 🌐 Option 1: Netlify (Recommended)

### Frontend Deployment

1. **Prepare the Repository**
   ```bash
   git add .
   git commit -m "Add Netlify frontend"
   git push origin main
   ```

2. **Deploy to Netlify**
   - Go to [netlify.com](https://netlify.com)
   - Click "New site from Git"
   - Connect your GitHub repository
   - Configure build settings:
     - **Build command**: `cd frontend && npm run build`
     - **Publish directory**: `frontend/build`
     - **Node version**: `18`

3. **Set Environment Variables**
   - Go to Site settings > Environment variables
   - Add: `REACT_APP_API_URL=https://your-api-domain.com`

4. **Deploy**
   - Click "Deploy site"
   - Wait for build to complete
   - Your app will be live at `https://your-site-name.netlify.app`

### Backend Deployment (Render)

1. **Prepare Backend**
   ```bash
   # Ensure your backend is in the root directory
   # Make sure requirements.txt is up to date
   ```

2. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Create new Web Service
   - Connect your GitHub repository
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python api/main.py`
     - **Environment**: Python 3.9

3. **Set Environment Variables**
   - Add any required environment variables
   - Set CORS origins to include your Netlify domain

### Backend Deployment (Fly.io)

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Initialize Fly App**
   ```bash
   cd your-project
   fly launch
   ```

3. **Deploy**
   ```bash
   fly deploy
   ```

## 🌐 Option 2: Streamlit Cloud

### Full Stack Deployment

1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set deployment settings:
     - **Main file**: `streamlit_app/app.py`
     - **Python version**: 3.9
   - Deploy!

3. **Deploy Backend Separately**
   - Use Render, Fly.io, or Railway for the FastAPI backend
   - Update API URL in Streamlit app

## 🐳 Option 3: Docker Deployment

### Local Docker

```bash
# Build and run with Docker Compose
docker-compose -f infra/docker-compose.yml up --build

# Services will be available at:
# - API: http://localhost:8000
# - Streamlit: http://localhost:8501
```

### Cloud Docker (Railway)

1. **Prepare for Railway**
   ```bash
   # Create railway.json in project root
   echo '{"build": {"builder": "DOCKERFILE", "dockerfilePath": "infra/Dockerfile"}}' > railway.json
   ```

2. **Deploy to Railway**
   - Go to [railway.app](https://railway.app)
   - Connect GitHub repository
   - Deploy automatically

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `https://api.yourdomain.com` |
| `API_HOST` | API host (backend) | `0.0.0.0` |
| `API_PORT` | API port (backend) | `8000` |

### CORS Configuration

Update your FastAPI backend to allow your frontend domain:

```python
# In api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local React dev
        "https://your-site.netlify.app",  # Netlify
        "https://your-streamlit-app.streamlit.app",  # Streamlit Cloud
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📊 Monitoring

### Health Checks

- **API Health**: `GET /health`
- **Frontend Health**: Built-in React error boundaries

### Logs

- **Netlify**: Site settings > Functions > Logs
- **Render**: Dashboard > Logs
- **Streamlit Cloud**: Built-in logs in dashboard

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check CORS configuration in backend
   - Verify frontend URL is in allowed origins

2. **API Connection Failed**
   - Verify API URL in environment variables
   - Check if backend is running and accessible
   - Test API endpoints directly

3. **Build Failures**
   - Check Node.js version (18+)
   - Verify all dependencies are installed
   - Check for TypeScript/JavaScript errors

4. **Deployment Timeouts**
   - Increase build timeout in platform settings
   - Optimize build process
   - Check for large dependencies

### Debug Commands

```bash
# Test API locally
curl http://localhost:8000/health

# Test frontend build
cd frontend && npm run build

# Check environment variables
echo $REACT_APP_API_URL
```

## 🔄 CI/CD Pipeline

### GitHub Actions

The project includes a GitHub Actions workflow (`.github/workflows/ci.yml`) that:

- Runs tests on multiple Python versions
- Checks code quality with flake8, black, isort
- Builds Docker images
- Runs security scans

### Automatic Deployment

Configure automatic deployment:

1. **Netlify**: Automatic on push to main branch
2. **Render**: Automatic on push to main branch
3. **Streamlit Cloud**: Automatic on push to main branch

## 📈 Performance Optimization

### Frontend

- Enable gzip compression
- Use CDN for static assets
- Implement lazy loading
- Optimize images

### Backend

- Use production WSGI server (Gunicorn)
- Enable caching
- Optimize database queries
- Use connection pooling

## 🔒 Security

### Production Checklist

- [ ] Use HTTPS everywhere
- [ ] Set secure environment variables
- [ ] Enable CORS properly
- [ ] Use production WSGI server
- [ ] Enable security headers
- [ ] Regular dependency updates
- [ ] Monitor for vulnerabilities

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review platform-specific documentation
3. Check logs for error messages
4. Create an issue on GitHub

## 🎉 Success!

Once deployed, your Amazon Review Intelligence Suite will be available at:

- **Frontend**: Your chosen platform URL
- **API**: Your backend URL
- **Documentation**: `{backend_url}/docs`

Enjoy your AI-powered Amazon review analysis system! 🛍️🤖
