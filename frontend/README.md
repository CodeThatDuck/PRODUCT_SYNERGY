# IBM DB2 Migration Command Center - Frontend

A professional React-based dashboard for visualizing Oracle to DB2 database migration using IBM Carbon Design System principles.

## 🎨 Design Philosophy

- **IBM Carbon Design System**: Clean, professional interface with IBM Blue (#0062ff) accents
- **White Background**: Professional, enterprise-grade appearance
- **Tailwind CSS**: Utility-first styling for rapid development
- **Lucide React Icons**: Clean, modern iconography

## 🚀 Features

### 1. Migration Dashboard (Home)
- **System Health Monitor**: Real-time pulse indicator showing DB2 container connectivity
- **Value Cards**: 
  - Total Tables Identified
  - Compatibility Score (100%)
  - Estimated TCO Savings ($420K)
  - Data Types Mapped (28)
- **Table Compatibility Matrix**: Visual heatmap of all tables with:
  - Column counts
  - Foreign key relationships
  - Status indicators (Ready/Minor Mapping)

### 2. SQL Diff Viewer
- **Side-by-Side Comparison**: 
  - Left Panel: Legacy Oracle SQL
  - Right Panel: Modern DB2 SQL
- **Syntax Highlighting**: Code highlighting for better readability
- **Zero-Change Proof**: Visual demonstration of compatibility

### 3. TCO Calculator
- **Interactive Bar Chart**: Visual comparison of Oracle vs DB2 costs
- **Dynamic Savings Calculator**: 
  - Adjustable license count slider (1-50 licenses)
  - Real-time cost calculations
  - 70% savings demonstration
- **Cost Breakdown Panel**:
  - Oracle Licensing: $600K/year
  - DB2 Licensing: $180K/year
  - Migration Cost: $50K (one-time)
  - ROI Timeline: 6 months

### 4. Live Data Audit
- **Validation Table**: Shows migrated records with:
  - Source table name
  - Record ID
  - Data type
  - Oracle value
  - DB2 value
  - Verification status (green checkmark)
- **Trust Badges**: Visual confirmation of data integrity

## 🛠️ Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js**: Interactive charts for TCO visualization
- **Axios**: HTTP client for API communication
- **Lucide React**: Beautiful icon library

## 📦 Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔌 API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000`:

- **Health Check**: `GET /api/health` - System status
- **Table Mappings**: Loaded from `/database/migrations/table_mappings.json`
- **Schema Files**: 
  - Oracle: `/database/schemas/oracle_source_schema.sql`
  - DB2: `/database/schemas/db2_generated_schema.sql`

## 🎯 Key Components

### StatCard
Displays key metrics with gradient backgrounds and icons.

### TableCard
Shows individual table information with compatibility status.

### CodePanel
Displays SQL code with syntax highlighting and line numbers.

### DashboardTab
Main overview with stats and compatibility matrix.

### DiffViewerTab
Side-by-side SQL comparison viewer.

### TCOCalculatorTab
Interactive cost analysis with charts and sliders.

### DataAuditTab
Data validation table with verification status.

## 🎨 Color Palette (IBM Carbon)

```css
--ibm-blue: #0062ff        /* Primary brand color */
--ibm-blue-hover: #0050e6  /* Hover state */
--ibm-blue-light: #e0f0ff  /* Light backgrounds */
--ibm-gray-10: #f4f4f4     /* Light gray */
--ibm-gray-20: #e0e0e0     /* Borders */
--ibm-gray-50: #8d8d8d     /* Secondary text */
--ibm-gray-100: #161616    /* Primary text */
--ibm-green: #24a148       /* Success states */
--ibm-yellow: #f1c21b      /* Warning states */
--ibm-red: #da1e28         /* Error states */
```

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- Desktop (1400px+)
- Tablet (768px - 1399px)
- Mobile (< 768px)

## 🔥 Performance

- **Fast Refresh**: Instant updates during development
- **Code Splitting**: Optimized bundle sizes
- **Lazy Loading**: Components loaded on demand
- **Optimized Images**: Efficient asset loading

## 🎓 Usage

1. **Start Backend**: Ensure FastAPI server is running on port 8000
2. **Start Frontend**: Run `npm run dev` to start on port 3000
3. **Navigate**: Use the tab navigation to explore different features
4. **Interact**: Adjust the TCO calculator slider to see cost projections

## 📊 Data Flow

```
User Interface (React)
    ↓
API Calls (Axios)
    ↓
FastAPI Backend (Port 8000)
    ↓
Database/File System
```

## 🚀 Deployment

For production deployment:

```bash
# Build optimized production bundle
npm run build

# The dist/ folder contains the production-ready files
# Deploy to any static hosting service (Vercel, Netlify, etc.)
```

## 🤝 Contributing

This is part of the Project Synergy Oracle to DB2 migration tool. The frontend provides the visual interface for the migration process.

## 📄 License

Part of the Project Synergy migration toolkit.

## 🎯 Future Enhancements

- Real-time migration progress tracking
- WebSocket integration for live updates
- Export reports to PDF
- Advanced filtering and search
- Migration history timeline
- Performance metrics dashboard
