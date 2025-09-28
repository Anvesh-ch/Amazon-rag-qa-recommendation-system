# Amazon Review Intelligence Suite - React Frontend

A modern React-based frontend for the Amazon Review Intelligence Suite, designed for Netlify deployment.

## 🚀 Features

- **Modern React 18** with hooks and functional components
- **Styled Components** for CSS-in-JS styling
- **React Query** for data fetching and caching
- **Responsive Design** that works on all devices
- **Real-time API Integration** with the FastAPI backend
- **Interactive Charts** using Recharts
- **Error Boundaries** for graceful error handling
- **Loading States** and user feedback
- **Accessibility** features built-in

## 🛠️ Development

### Prerequisites

- Node.js 18+
- npm or yarn
- Running FastAPI backend

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp env.example .env

# Edit .env file with your API URL
# REACT_APP_API_URL=http://localhost:8000
```

### Running Locally

```bash
# Start development server
npm start

# The app will be available at http://localhost:3000
```

### Building for Production

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview
```

## 🌐 Netlify Deployment

### Automatic Deployment

1. **Connect to GitHub**
   - Push your code to GitHub
   - Connect your repository to Netlify
   - Netlify will automatically build and deploy

2. **Configure Build Settings**
   - Build command: `npm run build`
   - Publish directory: `build`
   - Node version: `18`

3. **Set Environment Variables**
   - Go to Site settings > Environment variables
   - Add `REACT_APP_API_URL` with your API URL

### Manual Deployment

```bash
# Build the project
npm run build

# Deploy to Netlify
npx netlify deploy --prod --dir=build
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:8000` |
| `NODE_ENV` | Environment | `development` |

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── Header.js
│   │   ├── Sidebar.js
│   │   ├── QATab.js
│   │   ├── RecommendationsTab.js
│   │   ├── LoadingSpinner.js
│   │   └── ErrorBoundary.js
│   ├── hooks/
│   │   └── useAPIHealth.js
│   ├── services/
│   │   └── api.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── netlify.toml
├── package.json
└── README.md
```

## 🎨 Components

### Main Components

- **App.js**: Main application component with routing and theme
- **Header.js**: Top navigation with status indicator
- **Sidebar.js**: Side navigation with system stats
- **QATab.js**: Question answering interface
- **RecommendationsTab.js**: Product recommendations interface

### Utility Components

- **LoadingSpinner.js**: Loading state component
- **ErrorBoundary.js**: Error handling component

## 🔧 API Integration

The frontend communicates with the FastAPI backend through:

- **Question Answering**: `/ask_review/ask`
- **Similar Reviews**: `/ask_review/similar`
- **Product Recommendations**: `/recommend/products`
- **Categories**: `/recommend/categories`
- **Health Check**: `/health`

## 🎯 Features

### Question Answering
- Natural language questions about Amazon reviews
- AI-generated answers with source citations
- Configurable number of sources
- Real-time processing feedback

### Product Recommendations
- Text-based product search
- Similar product recommendations
- Category-based top products
- Interactive charts and analytics
- Review snippet previews

### User Experience
- Responsive design for all devices
- Real-time API health monitoring
- Loading states and error handling
- Smooth animations and transitions
- Accessible interface

## 🚀 Performance

- **Code Splitting**: Automatic code splitting with React.lazy
- **Caching**: React Query for intelligent data caching
- **Optimization**: Production build optimizations
- **CDN**: Static assets served via Netlify CDN

## 🔒 Security

- **CORS**: Properly configured for API communication
- **Headers**: Security headers configured in netlify.toml
- **Environment**: Sensitive data in environment variables
- **Validation**: Input validation and sanitization

## 📱 Mobile Support

- **Responsive Design**: Works on all screen sizes
- **Touch Friendly**: Optimized for touch interactions
- **Progressive Web App**: PWA capabilities
- **Offline Support**: Basic offline functionality

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test -- --coverage

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix
```

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if backend is running on correct port
   - Verify REACT_APP_API_URL environment variable
   - Check CORS settings on backend

2. **Build Fails**
   - Ensure Node.js 18+ is installed
   - Clear node_modules and reinstall
   - Check for TypeScript errors

3. **Deployment Issues**
   - Verify netlify.toml configuration
   - Check environment variables in Netlify
   - Review build logs in Netlify dashboard

### Debug Mode

```bash
# Enable debug logging
REACT_APP_DEBUG=true npm start
```

## 📈 Analytics

The app is ready for analytics integration:

- Google Analytics
- Mixpanel
- Sentry for error tracking
- Custom analytics events

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
