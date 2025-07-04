# SP-API Testing Dashboard

A comprehensive React frontend for testing the Amazon SP-API Mock backend with session management, test flow validation, and database monitoring.

## Features

- **Session Management**: Create and manage isolated testing sessions
- **Test Flows**: Browse and execute predefined test scenarios
- **Validation**: Validate test flow results with detailed feedback
- **Database Monitoring**: View current database state and statistics
- **Tools & Utilities**: Reset database, test connections, and export data

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API communication
- **React Query** for data fetching and caching

## Prerequisites

- Node.js 16+ and npm
- Backend server running on `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### 1. Session Management
- **Create Session**: Generate a new isolated testing session
- **Input Session**: Use an existing session ID
- **Session Validation**: Automatic validation of session format and existence

### 2. Test Flows
- **Browse Flows**: View all available test scenarios
- **Filter & Search**: Find specific flows by category or keywords
- **Copy Instructions**: Copy Claude instructions to clipboard
- **Flow Categories**: Create, Update, Delete, Search, Bulk Operations, Analysis

### 3. Validation
- **Individual Validation**: Test specific flows
- **Bulk Validation**: Test all flows at once
- **Detailed Results**: View pass/fail status with detailed feedback
- **Success Metrics**: Track validation success rates

### 4. Database State
- **Overview Statistics**: Total listings, active/inactive counts
- **Price Analytics**: Min, max, average pricing
- **Seller Breakdown**: Listings per seller
- **Inventory Tracking**: Total units in stock
- **Visual Progress**: Status distribution charts

### 5. Tools & Utilities
- **Database Reset**: Restore to original seed state
- **Connection Testing**: Verify backend connectivity
- **Data Export**: Export session information
- **Quick Links**: Access API documentation

## API Integration

The frontend communicates with the FastAPI backend using:
- **Base URL**: `http://localhost:8000`
- **Session Header**: `X-Session-ID` for authenticated requests
- **Error Handling**: Automatic session validation and error feedback
- **Health Checks**: Backend connectivity monitoring

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── common/       # Layout components
│   │   ├── session/      # Session management
│   │   ├── flows/        # Test flow components
│   │   ├── validation/   # Validation components
│   │   ├── database/     # Database state components
│   │   └── tools/        # Utility components
│   ├── contexts/         # React contexts
│   ├── hooks/            # Custom React hooks
│   ├── pages/            # Page components
│   ├── services/         # API service layer
│   ├── types/            # TypeScript type definitions
│   ├── utils/            # Utility functions
│   └── App.tsx           # Main application component
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Workflow

### Testing Workflow
1. **Start Backend**: Ensure FastAPI server is running on port 8000
2. **Create Session**: Generate or input a session ID
3. **Browse Flows**: Select test scenarios from the flows page
4. **Execute Tests**: Ask Claude to perform the actions described in flow instructions
5. **Validate Results**: Use the validation page to check if tests passed
6. **Reset Database**: Use tools page to reset between tests
7. **Monitor State**: Check database page for current data state

### Development Workflow
1. **Hot Reload**: Vite provides instant feedback during development
2. **Type Safety**: TypeScript ensures type safety across the application
3. **Linting**: ESLint maintains code quality
4. **Component Structure**: Modular components for maintainability

## Configuration

### Environment Variables
Create a `.env` file in the frontend directory for custom configuration:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=SP-API Testing Dashboard
```

### Tailwind Configuration
The `tailwind.config.js` includes custom color schemes:
- **Primary**: Blue tones for actions and navigation
- **Success**: Green for passed validations
- **Error**: Red for failed validations and errors
- **Warning**: Yellow/Orange for warnings

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure FastAPI server is running on port 8000
   - Check CORS configuration in backend
   - Verify network connectivity

2. **Session Invalid**
   - Session may have expired or been deleted
   - Create a new session from the dashboard
   - Check session ID format (session_xxxxxxxxxxxx)

3. **Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility
   - Verify all dependencies are installed

4. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check for conflicting CSS classes
   - Verify PostCSS configuration

### Performance Tips

- Use React Query for efficient data caching
- Implement proper loading states for better UX
- Optimize bundle size with code splitting
- Use React.memo for expensive components

## Contributing

1. Follow the existing code structure and naming conventions
2. Add TypeScript types for all new interfaces
3. Include proper error handling and loading states
4. Test components with different session states
5. Update documentation for new features

## License

This project is part of the SP-API Mock testing framework.
