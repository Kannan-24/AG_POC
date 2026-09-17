# A&G RBAC + Multi-Tenant POC Frontend

React 18 application for the A&G RBAC POC.

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

```bash
cd frontend
npm install
```

### Configuration

The frontend looks for the API backend at `http://localhost:8000` by default.

To change this, set the `REACT_APP_API_URL` environment variable:

```bash
export REACT_APP_API_URL=http://your-api-server:8000
```

### Running the App

```bash
npm start
```

Opens [http://localhost:3000](http://localhost:3000) to view it in your browser.

### Building for Production

```bash
npm run build
```

### Running Tests

```bash
npm test
```

## Project Structure

```
src/
├── components/        # Shared UI components
├── pages/            # Page components
├── auth/             # Authentication context and helpers
├── services/         # API client
├── hooks/            # Custom hooks (permissions, etc.)
├── styles/           # CSS stylesheets
└── utils/            # Utility functions
```

## Features

- Multi-tenant SaaS application
- Role-based access control (RBAC)
- Permission-based UI
- Audit logging
- Cases management
- User and roles display
- Clean, responsive UI

## Demo Users

### Tenant: Prominence Health

- **Alice** - A&G Specialist
  - Permissions: view_cases, create_case, edit_case, reassign_case
- **Mike** - Medical Director
  - Permissions: view_cases, sign_decision

### Tenant: Demo Health Plan

- **Bob** - Supervisor
  - Permissions: view_cases, reassign_case, view_audit
- **Sara** - Tenant Administrator
  - Permissions: view_cases, create_case, edit_case, reassign_case, view_audit, configure_tenant
