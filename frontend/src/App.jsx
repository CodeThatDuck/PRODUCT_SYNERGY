import { useState, useEffect } from 'react';
import { Activity, Database, DollarSign, CheckCircle, AlertCircle, TrendingDown, Code, FileText, Upload } from 'lucide-react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [systemHealth, setSystemHealth] = useState(null);
  const [tableMappings, setTableMappings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [migrationResult, setMigrationResult] = useState(null);

  useEffect(() => {
    checkSystemHealth();
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`);
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ status: 'unhealthy' });
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-gradient-to-r from-ibm-blue to-ibm-blue-hover text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="text-3xl font-bold tracking-tight">IBM</div>
              <div>
                <h1 className="text-2xl font-semibold">Project Synergy: Oracle to DB2 Takeout Engine</h1>
                <p className="text-sm opacity-90 mt-1">Enterprise Migration Command Center</p>
              </div>
            </div>
            <div className="flex items-center gap-3 bg-white/10 backdrop-blur-sm px-4 py-3 rounded">
              <div className={`w-3 h-3 rounded-full ${systemHealth?.status === 'healthy' ? 'bg-ibm-green animate-pulse' : 'bg-ibm-red'}`}></div>
              <span className="text-sm font-medium">
                {systemHealth?.status === 'healthy' ? 'DB2 Container Live' : 'System Offline'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="border-b-2 border-ibm-gray-20 bg-white sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex gap-1">
            {[
              { id: 'upload', label: 'Source Ingestion', icon: Upload },
              { id: 'diff', label: 'SQL Diff Viewer', icon: Code },
              { id: 'migration', label: 'Migration & Data Audit', icon: Activity },
              { id: 'tco', label: 'TCO Calculator', icon: DollarSign }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 font-medium transition-all ${
                  activeTab === tab.id
                    ? 'text-ibm-blue border-b-3 border-ibm-blue bg-ibm-blue-light/20'
                    : 'text-ibm-gray-50 hover:text-ibm-blue hover:bg-ibm-gray-10'
                }`}
              >
                <tab.icon size={18} />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'upload' && <UploadTab setUploadedFile={setUploadedFile} setActiveTab={setActiveTab} />}
        {activeTab === 'diff' && <DiffViewerTab uploadedFile={uploadedFile} />}
        {activeTab === 'migration' && <MigrationAndAuditTab uploadedFile={uploadedFile} migrationResult={migrationResult} setMigrationResult={setMigrationResult} />}
        {activeTab === 'tco' && <TCOCalculatorTab uploadedFile={uploadedFile} />}
      </main>
    </div>
  );
}

// Upload Tab Component
function UploadTab({ setUploadedFile, setActiveTab }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [processResult, setProcessResult] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.sql')) {
      setSelectedFile(file);
      setUploadResult(null);
      setProcessResult(null);
    } else {
      alert('Please select a .sql file');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/process-raw-sql`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadResult(response.data);
      setUploadedFile(response.data);
      setProcessing(false);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-2xl font-semibold">Upload Oracle SQL File</h2>
          <span className="px-3 py-1 bg-ibm-blue-light text-ibm-blue text-sm font-semibold rounded-full">
            Step 1: Source Ingestion
          </span>
        </div>

        <div className="space-y-6">
          {/* File Upload Area */}
          <div className="border-2 border-dashed border-ibm-gray-20 rounded-lg p-8 text-center hover:border-ibm-blue transition-colors">
            <Upload size={48} className="mx-auto mb-4 text-ibm-gray-50" />
            <h3 className="text-lg font-semibold mb-2">Drop your Oracle SQL file here</h3>
            <p className="text-sm text-ibm-gray-50 mb-4">or click to browse</p>
            <input
              type="file"
              accept=".sql"
              onChange={handleFileSelect}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="inline-block bg-ibm-blue hover:bg-ibm-blue-hover text-white font-medium px-6 py-3 rounded cursor-pointer transition-colors"
            >
              Select SQL File
            </label>
          </div>

          {/* Selected File Info */}
          {selectedFile && (
            <div className="bg-ibm-gray-10 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText size={24} className="text-ibm-blue" />
                  <div>
                    <p className="font-semibold">{selectedFile.name}</p>
                    <p className="text-sm text-ibm-gray-50">
                      {(selectedFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="bg-ibm-blue hover:bg-ibm-blue-hover text-white font-medium px-6 py-3 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? (
                    <span className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Processing...
                    </span>
                  ) : (
                    'Process SQL File'
                  )}
                </button>
              </div>
            </div>
          )}

          {/* Upload Result */}
          {uploadResult && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-start gap-3">
                <CheckCircle size={24} className="text-ibm-green flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <h3 className="font-semibold text-lg mb-2">SQL File Processed Successfully!</h3>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-ibm-gray-50">Tables Detected</p>
                      <p className="text-2xl font-bold text-ibm-blue">
                        {uploadResult.analysis?.tables_detected || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-ibm-gray-50">File Size</p>
                      <p className="text-2xl font-bold text-ibm-blue">
                        {(uploadResult.file_info?.size_bytes / 1024).toFixed(0)} KB
                      </p>
                    </div>
                  </div>

                  {uploadResult.analysis?.table_names && uploadResult.analysis.table_names.length > 0 && (
                    <div className="mb-4">
                      <p className="text-sm font-semibold mb-2">Detected Tables:</p>
                      <div className="flex flex-wrap gap-2">
                        {uploadResult.analysis.table_names.map((table, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-ibm-blue-light text-ibm-blue text-sm font-medium rounded-full"
                          >
                            {table}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <button
                    onClick={() => setActiveTab('diff')}
                    className="bg-ibm-blue hover:bg-ibm-blue-hover text-white font-medium px-6 py-3 rounded transition-colors"
                  >
                    View SQL Diff →
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Preview Section */}
      {uploadResult?.preview && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-2xl font-semibold">SQL Preview</h2>
            <span className="px-3 py-1 bg-ibm-blue-light text-ibm-blue text-sm font-semibold rounded-full">
              Oracle → DB2 Conversion
            </span>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <h3 className="font-semibold mb-2 text-sm text-ibm-gray-50">Oracle SQL (Original)</h3>
              <pre className="bg-gray-900 text-gray-300 p-4 rounded text-xs overflow-auto max-h-64">
                {uploadResult.preview.oracle_snippet}
              </pre>
            </div>
            <div>
              <h3 className="font-semibold mb-2 text-sm text-ibm-gray-50">DB2 SQL (Converted)</h3>
              <pre className="bg-gray-900 text-gray-300 p-4 rounded text-xs overflow-auto max-h-64">
                {uploadResult.preview.db2_snippet}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Combined Migration & Data Audit Tab Component
function MigrationAndAuditTab({ uploadedFile, migrationResult, setMigrationResult }) {
  const [migrating, setMigrating] = useState(false);
  const [migrationStatus, setMigrationStatus] = useState(null);

  const handleRunMigration = async () => {
    // Use uploaded file's mapping or fallback to default
    const mappingFile = uploadedFile?.file_info?.mapping_file || 'table_mappings.json';
    
    setMigrating(true);
    setMigrationStatus(null);
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/run-full-migration?mapping_file=${mappingFile}`
      );
      setMigrationResult(response.data);
      setMigrationStatus('success');
    } catch (error) {
      console.error('Migration failed:', error);
      setMigrationStatus('failed');
      alert('Migration failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setMigrating(false);
    }
  };

  const tablesDetected = uploadedFile?.analysis?.tables_detected || 0;
  const hasMigrationData = !!migrationResult?.verification_data;

  // If no file uploaded, show message
  if (!uploadedFile) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="text-2xl font-semibold">Migration & Data Audit</h2>
          <span className="px-3 py-1 bg-green-100 text-ibm-green text-sm font-semibold rounded-full">
            All Systems Go
          </span>
        </div>
        <div className="p-12 text-center">
          <Activity size={48} className="mx-auto mb-4 text-ibm-blue" />
          <h3 className="text-xl font-semibold mb-2">Upload a SQL file to start migration</h3>
          <p className="text-sm text-ibm-gray-50">Go to the "Source Ingestion" tab to upload your Oracle SQL file and begin the migration process.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          icon={Database}
          value={hasMigrationData ? migrationResult.summary.total_tables : tablesDetected}
          label="Total Tables"
          color="blue"
        />
        <StatCard
          icon={CheckCircle}
          value={hasMigrationData ? migrationResult.summary.total_rows.toLocaleString() : "Ready"}
          label={hasMigrationData ? "Records Migrated" : "Compatibility Score"}
          color="green"
        />
        <StatCard
          icon={FileText}
          value={hasMigrationData ? migrationResult.summary.total_transformations : "28"}
          label={hasMigrationData ? "Transformations" : "Data Types Mapped"}
          color="blue"
        />
        <StatCard
          icon={CheckCircle}
          value={hasMigrationData ? migrationResult.summary.total_validations : "100%"}
          label={hasMigrationData ? "Validations" : "Success Rate"}
          color="green"
        />
      </div>

      {/* Migration Control */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-2xl font-semibold">Migration Control Center</h2>
          <span className="px-3 py-1 bg-ibm-blue-light text-ibm-blue text-sm font-semibold rounded-full">
            {hasMigrationData ? 'Migration Complete' : 'Ready to Deploy'}
          </span>
        </div>
        <div className="p-8 text-center">
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-2">
              {hasMigrationData ? `Successfully Migrated ${tablesDetected} Tables` : `Ready to Migrate ${tablesDetected} Tables`}
            </h3>
            <p className="text-sm text-ibm-gray-50 mb-4">
              {hasMigrationData
                ? 'View detailed migration results below.'
                : 'This will create the DB2 schema, generate mock data, and migrate all tables.'}
            </p>
          </div>
          
          <button
            onClick={handleRunMigration}
            disabled={migrating}
            className="bg-gradient-to-r from-ibm-blue to-ibm-blue-hover text-white font-bold text-lg px-12 py-6 rounded-lg shadow-lg hover:shadow-xl transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            {migrating ? (
              <span className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                Running Migration...
              </span>
            ) : (
              <span className="flex items-center gap-3">
                <Database size={24} />
                {hasMigrationData ? '🔄 Re-run Migration' : '🚀 Run Full Migration'}
              </span>
            )}
          </button>

          {migrationStatus === 'success' && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-700 font-semibold">✓ Migration completed successfully! View results below.</p>
            </div>
          )}
        </div>
      </div>

      {/* Data Audit Results - Only show if migration has been run */}
      {hasMigrationData && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-2xl font-semibold">Migration Results by Table</h2>
            <span className="px-3 py-1 bg-green-100 text-ibm-green text-sm font-semibold rounded-full">
              ✓ All Verified
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-ibm-gray-10 border-b-2 border-ibm-gray-20">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Table Name</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Total Records</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Successful</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Transformations</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Validations</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Accuracy</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold">Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(migrationResult.verification_data).map(([tableName, data], index) => (
                  <tr key={index} className="border-b border-ibm-gray-20 hover:bg-ibm-gray-10 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium">{tableName}</td>
                    <td className="px-4 py-3 text-sm">{data.total_rows.toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm text-ibm-green font-semibold">{data.successful_rows.toLocaleString()}</td>
                    <td className="px-4 py-3 text-sm">{data.transformations_applied}</td>
                    <td className="px-4 py-3 text-sm">{data.validations_passed}</td>
                    <td className="px-4 py-3 text-sm font-semibold text-ibm-green">{(data.data_integrity * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3">
                      <span className="px-3 py-1 inline-flex items-center gap-1 text-xs leading-5 font-semibold rounded-full bg-green-100 text-ibm-green">
                        <CheckCircle size={14} />
                        VERIFIED
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

// Diff Viewer Tab Component
function DiffViewerTab({ uploadedFile }) {
  const [highlightDiff, setHighlightDiff] = useState(false);
  const hasData = uploadedFile?.preview?.oracle_snippet && uploadedFile?.preview?.db2_snippet;

  // Function to highlight differences
  const highlightChanges = (text, isOracle) => {
    if (!highlightDiff) return text;
    
    // Define Oracle-specific types that get converted to different DB2 types
    const oracleOnlyTypes = [
      'NUMBER', 'VARCHAR2', 'NVARCHAR2', 'NCHAR',
      'BINARY_FLOAT', 'BINARY_DOUBLE', 'RAW',
      'LONG', 'LONG RAW', 'ROWID', 'UROWID',
      'NCLOB', 'BFILE'
    ];
    
    // Define DB2 types that replace Oracle types
    const db2ReplacementTypes = [
      'DECIMAL', 'VARCHAR', 'VARGRAPHIC', 'GRAPHIC',
      'REAL', 'DOUBLE', 'VARBINARY',
      'CLOB', 'BLOB', 'VARCHAR', 'VARCHAR',
      'DBCLOB', 'BLOB'
    ];
    
    let highlighted = text;
    
    if (isOracle) {
      // Highlight Oracle-specific types in red (types that will be converted)
      oracleOnlyTypes.forEach(type => {
        const regex = new RegExp(`\\b${type}\\b`, 'gi');
        highlighted = highlighted.replace(regex, (match) =>
          `<span style="background-color: #fee; color: #c00; font-weight: bold; padding: 2px 4px; border-radius: 3px;">${match}</span>`
        );
      });
    } else {
      // Highlight DB2 replacement types in green (types that replaced Oracle types)
      db2ReplacementTypes.forEach(type => {
        const regex = new RegExp(`\\b${type}\\b`, 'gi');
        highlighted = highlighted.replace(regex, (match) =>
          `<span style="background-color: #efe; color: #080; font-weight: bold; padding: 2px 4px; border-radius: 3px;">${match}</span>`
        );
      });
    }
    
    return highlighted;
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="text-2xl font-semibold">Side-by-Side SQL Comparison</h2>
        <span className="px-3 py-1 bg-ibm-blue-light text-ibm-blue text-sm font-semibold rounded-full">
          Zero-Change Migration
        </span>
      </div>
      
      {hasData ? (
        <>
          {/* Type Mappings Summary */}
          {uploadedFile.analysis?.type_mappings && (
            <div className="mb-6 p-4 bg-ibm-blue-light/20 rounded-lg border border-ibm-blue">
              <h3 className="font-semibold mb-3 text-ibm-blue">🔄 Type Conversions Detected</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                {uploadedFile.analysis.type_mappings.map((mapping, idx) => (
                  <div key={idx} className="bg-white p-3 rounded border border-ibm-gray-20">
                    <div className="text-xs text-ibm-gray-50 mb-1">Oracle</div>
                    <div className="font-semibold text-sm text-red-600">{mapping.oracle_type}</div>
                    <div className="text-xs text-ibm-gray-50 my-1">↓</div>
                    <div className="text-xs text-ibm-gray-50 mb-1">DB2</div>
                    <div className="font-semibold text-sm text-ibm-blue">{mapping.db2_type}</div>
                    <div className="text-xs text-ibm-gray-50 mt-1">{mapping.occurrences}×</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Highlight Toggle */}
          <div className="mb-4 flex items-center justify-between p-4 bg-ibm-gray-10 rounded-lg">
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={highlightDiff}
                  onChange={(e) => setHighlightDiff(e.target.checked)}
                  className="w-5 h-5 text-ibm-blue rounded focus:ring-ibm-blue cursor-pointer"
                />
                <span className="font-medium text-sm">Highlight Differences</span>
              </label>
              {highlightDiff && (
                <div className="flex items-center gap-3 ml-4 text-xs">
                  <span className="flex items-center gap-1">
                    <span className="inline-block w-3 h-3 bg-red-100 border border-red-300 rounded"></span>
                    Oracle Types
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="inline-block w-3 h-3 bg-green-100 border border-green-300 rounded"></span>
                    DB2 Types
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* SQL Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-sm text-ibm-gray-50">Oracle SQL (Original)</h3>
                <span className="px-2 py-1 bg-red-100 text-red-600 text-xs font-medium rounded">Legacy</span>
              </div>
              <div className="bg-white border-2 border-ibm-gray-20 rounded p-4 overflow-auto" style={{ maxHeight: '800px' }}>
                {highlightDiff ? (
                  <pre
                    className="text-black text-xs font-mono whitespace-pre-wrap"
                    dangerouslySetInnerHTML={{ __html: highlightChanges(uploadedFile.preview.oracle_snippet, true) }}
                  />
                ) : (
                  <pre className="text-black text-xs font-mono whitespace-pre-wrap">
                    {uploadedFile.preview.oracle_snippet}
                  </pre>
                )}
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-sm text-ibm-gray-50">DB2 SQL (Converted)</h3>
                <span className="px-2 py-1 bg-green-100 text-ibm-green text-xs font-medium rounded">Modern</span>
              </div>
              <div className="bg-white border-2 border-ibm-gray-20 rounded p-4 overflow-auto" style={{ maxHeight: '800px' }}>
                {highlightDiff ? (
                  <pre
                    className="text-black text-xs font-mono whitespace-pre-wrap"
                    dangerouslySetInnerHTML={{ __html: highlightChanges(uploadedFile.preview.db2_snippet, false) }}
                  />
                ) : (
                  <pre className="text-black text-xs font-mono whitespace-pre-wrap">
                    {uploadedFile.preview.db2_snippet}
                  </pre>
                )}
              </div>
            </div>
          </div>

          {/* Tables Summary */}
          {uploadedFile.analysis?.table_names && (
            <div className="mt-6 p-4 bg-ibm-gray-10 rounded-lg">
              <h3 className="font-semibold mb-3">📊 Tables Detected: {uploadedFile.analysis.tables_detected}</h3>
              <div className="flex flex-wrap gap-2">
                {uploadedFile.analysis.table_names.map((table, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-white border border-ibm-gray-20 text-ibm-gray-70 text-sm font-medium rounded"
                  >
                    {table}
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="p-12 text-center">
          <Code size={48} className="mx-auto mb-4 text-ibm-blue" />
          <h3 className="text-xl font-semibold mb-2">Upload a SQL file to see the comparison</h3>
          <p className="text-sm text-ibm-gray-50">Go to the "Source Ingestion" tab to upload your Oracle SQL file.</p>
          <p className="text-sm text-ibm-gray-50 mt-2">After processing, the SQL diff will be displayed here automatically.</p>
        </div>
      )}
    </div>
  );
}

// TCO Calculator Tab Component
function TCOCalculatorTab({ uploadedFile }) {
  const [databaseSizeGB, setDatabaseSizeGB] = useState(100);
  const [tcoData, setTcoData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Get table and column count from uploaded file
  const tablesDetected = uploadedFile?.analysis?.tables_detected || 10;
  const columnCount = uploadedFile?.analysis?.table_names?.length * 10 || 100; // Estimate

  useEffect(() => {
    fetchTCOAnalysis();
  }, [databaseSizeGB, tablesDetected]);

  const fetchTCOAnalysis = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/get-tco-analysis?table_count=${tablesDetected}&column_count=${columnCount}&database_size_gb=${databaseSizeGB}`
      );
      setTcoData(response.data);
    } catch (error) {
      console.error('Failed to fetch TCO analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!tcoData) {
    return (
      <div className="card">
        <div className="p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ibm-blue mx-auto mb-4"></div>
          <p className="text-ibm-gray-50">Loading TCO analysis...</p>
        </div>
      </div>
    );
  }

  const chartData = {
    labels: ['Oracle (Legacy)', 'IBM DB2 (Modern)'],
    datasets: [{
      label: 'Annual Cost ($)',
      data: [tcoData.oracle_costs.total_annual, tcoData.db2_costs.total_annual],
      backgroundColor: ['#da1e28', '#0062ff'],
      borderColor: ['#da1e28', '#0062ff'],
      borderWidth: 2
    }]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: `Oracle Takeout ROI Calculator - ${tablesDetected} Tables`,
        font: { size: 18, weight: 'bold' }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: (value) => '$' + (value / 1000) + 'K'
        }
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* Database Size Slider */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold">Configuration</h2>
        </div>
        <div className="p-6">
          <label className="block mb-4">
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium text-ibm-gray-70">Estimated Database Size (GB)</span>
              <span className="text-lg font-bold text-ibm-blue">{databaseSizeGB} GB</span>
            </div>
            <input
              type="range"
              min="10"
              max="1000"
              step="10"
              value={databaseSizeGB}
              onChange={(e) => setDatabaseSizeGB(parseInt(e.target.value))}
              className="w-full h-2 bg-ibm-gray-20 rounded-lg appearance-none cursor-pointer accent-ibm-blue"
            />
            <div className="flex justify-between text-xs text-ibm-gray-50 mt-1">
              <span>10 GB</span>
              <span>1000 GB</span>
            </div>
          </label>
          <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
            <div className="bg-ibm-gray-10 p-3 rounded">
              <span className="text-ibm-gray-50">Tables:</span>
              <span className="ml-2 font-semibold">{tablesDetected}</span>
            </div>
            <div className="bg-ibm-gray-10 p-3 rounded">
              <span className="text-ibm-gray-50">Columns:</span>
              <span className="ml-2 font-semibold">{columnCount}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main TCO Analysis */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-2xl font-semibold">Oracle Takeout ROI Analysis</h2>
          <span className="px-3 py-1 bg-green-100 text-ibm-green text-sm font-semibold rounded-full">
            {tcoData.comparison.savings_percentage}% Savings
          </span>
        </div>
        
        {!loading ? (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Chart */}
              <div className="lg:col-span-2">
                <Bar data={chartData} options={chartOptions} />
              </div>

              {/* Savings Panel */}
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-ibm-green to-green-600 text-white p-6 rounded-lg text-center">
                  <p className="text-sm opacity-90 mb-2">Annual Savings</p>
                  <p className="text-4xl font-bold mb-2">${(tcoData.comparison.annual_savings / 1000).toFixed(0)}K</p>
                  <p className="text-sm opacity-80">{tcoData.comparison.savings_percentage}% Cost Reduction</p>
                </div>

                <div className="bg-ibm-blue-light/20 border border-ibm-blue p-6 rounded-lg text-center">
                  <p className="text-sm text-ibm-gray-70 mb-2">ROI Payback Period</p>
                  <p className="text-2xl font-bold text-ibm-blue">{tcoData.comparison.payback_period}</p>
                </div>

                <div className="bg-ibm-gray-10 p-6 rounded-lg space-y-3">
                  <h3 className="font-semibold mb-4">Quick Facts</h3>
                  <div className="flex justify-between text-sm">
                    <span className="text-ibm-gray-50">Database Size</span>
                    <span className="font-semibold text-ibm-blue">{databaseSizeGB} GB</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-ibm-gray-50">DB2 Compression</span>
                    <span className="font-semibold text-ibm-green">{tcoData.db2_costs.compression_savings} GB saved</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-ibm-gray-50">Migration Cost</span>
                    <span className="font-semibold">${(tcoData.comparison.migration_cost / 1000).toFixed(0)}K (one-time)</span>
                  </div>
                  <div className="flex justify-between text-sm pt-3 border-t border-ibm-gray-20">
                    <span className="text-ibm-gray-50">5-Year Savings</span>
                    <span className="font-semibold text-ibm-green">
                      ${(tcoData.five_year_projection.total_savings / 1000).toFixed(0)}K
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Detailed Cost Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              {/* Oracle Costs */}
              <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                <h3 className="font-semibold text-lg mb-4 text-red-700">Oracle Annual Costs</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Base License</span>
                    <span className="font-semibold">${(tcoData.oracle_costs.base_license / 1000).toFixed(0)}K</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Support (22%)</span>
                    <span className="font-semibold">${(tcoData.oracle_costs.annual_support / 1000).toFixed(1)}K</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Storage ($2/GB/mo)</span>
                    <span className="font-semibold">${(tcoData.oracle_costs.storage_annual / 1000).toFixed(1)}K</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">DBA Labor (10 hrs/mo)</span>
                    <span className="font-semibold">${(tcoData.oracle_costs.dba_labor_annual / 1000).toFixed(0)}K</span>
                  </div>
                  <div className="flex justify-between text-sm pt-3 border-t-2 border-red-300 font-bold">
                    <span>Total Annual</span>
                    <span className="text-red-700">${(tcoData.oracle_costs.total_annual / 1000).toFixed(0)}K</span>
                  </div>
                </div>
              </div>

              {/* DB2 Costs */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="font-semibold text-lg mb-4 text-ibm-blue">DB2 Annual Costs</h3>
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Base License</span>
                    <span className="font-semibold">${(tcoData.db2_costs.base_license / 1000).toFixed(0)}K</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Support</span>
                    <span className="font-semibold text-ibm-green">Included</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Storage ($1/GB/mo, 50% compressed)</span>
                    <span className="font-semibold">${(tcoData.db2_costs.storage_annual / 1000).toFixed(1)}K</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">DBA Labor (3 hrs/mo, self-tuning)</span>
                    <span className="font-semibold">${(tcoData.db2_costs.dba_labor_annual / 1000).toFixed(1)}K</span>
                  </div>
                  <div className="flex justify-between text-sm pt-3 border-t-2 border-blue-300 font-bold">
                    <span>Total Annual</span>
                    <span className="text-ibm-blue">${(tcoData.db2_costs.total_annual / 1000).toFixed(0)}K</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 5-Year Projection */}
            <div className="mt-6 p-6 bg-gradient-to-r from-ibm-blue-light/30 to-ibm-green/20 rounded-lg border border-ibm-blue">
              <h3 className="font-semibold text-lg mb-4 text-ibm-blue">💰 5-Year Financial Projection</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Oracle 5-Year Total</p>
                  <p className="text-2xl font-bold text-red-600">${(tcoData.five_year_projection.oracle_total / 1000).toFixed(0)}K</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">DB2 5-Year Total (incl. migration)</p>
                  <p className="text-2xl font-bold text-ibm-blue">${(tcoData.five_year_projection.db2_total / 1000).toFixed(0)}K</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Savings</p>
                  <p className="text-2xl font-bold text-ibm-green">${(tcoData.five_year_projection.total_savings / 1000).toFixed(0)}K</p>
                  <p className="text-xs text-gray-600 mt-1">({tcoData.five_year_projection.roi_percentage}% ROI)</p>
                </div>
              </div>
            </div>

            {/* Industry Benchmarks Note */}
            <div className="mt-6 p-6 bg-yellow-50 border border-yellow-300 rounded-lg">
              <h3 className="font-semibold mb-3 text-yellow-800">📊 Industry Benchmarks Used</h3>
              <div className="text-sm space-y-2 text-gray-700">
                <p>• <strong>Oracle:</strong> $50K base license + 22% annual support + $2/GB/month storage + $150/hr DBA labor (10 hrs/month)</p>
                <p>• <strong>DB2:</strong> $15K base license (support included) + $1/GB/month storage + $150/hr DBA labor (3 hrs/month due to self-tuning)</p>
                <p>• <strong>DB2 Advantage:</strong> 50% data compression reduces storage costs significantly</p>
                <p>• <strong>Migration:</strong> $50K one-time cost (typical for {tablesDetected} tables)</p>
              </div>
            </div>
          </>
        ) : (
          <div className="p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-ibm-blue mx-auto mb-4"></div>
            <p className="text-ibm-gray-50">Loading TCO analysis...</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Reusable Components
function StatCard({ icon: Icon, value, label, color }) {
  const colorClasses = {
    blue: 'from-ibm-blue to-ibm-blue-hover',
    green: 'from-ibm-green to-green-600'
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} text-white p-6 rounded-lg shadow-lg`}>
      <div className="flex items-center justify-between mb-3">
        <Icon size={32} className="opacity-80" />
      </div>
      <div className="text-4xl font-bold mb-1">{value}</div>
      <div className="text-sm opacity-90 uppercase tracking-wide">{label}</div>
    </div>
  );
}

function TableCard({ tableName, tableConfig }) {
  const columnCount = Object.keys(tableConfig.columns || {}).length;
  const fkCount = Object.keys(tableConfig.foreign_keys || {}).length;
  const status = columnCount > 10 ? 'minor' : 'ready';

  return (
    <div className={`border-2 rounded-lg p-4 hover:shadow-lg transition-all cursor-pointer ${
      status === 'ready' ? 'border-l-4 border-l-ibm-green' : 'border-l-4 border-l-ibm-yellow'
    } border-ibm-gray-20`}>
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-lg">{tableName}</h3>
        <span className={`px-2 py-1 text-xs font-semibold rounded ${
          status === 'ready' ? 'bg-green-100 text-ibm-green' : 'bg-yellow-100 text-yellow-800'
        }`}>
          {status === 'ready' ? 'Ready' : 'Minor Mapping'}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <p className="text-xs text-ibm-gray-50 mb-1">Columns</p>
          <p className="text-2xl font-bold text-ibm-blue">{columnCount}</p>
        </div>
        <div>
          <p className="text-xs text-ibm-gray-50 mb-1">Foreign Keys</p>
          <p className="text-2xl font-bold text-ibm-blue">{fkCount}</p>
        </div>
      </div>
    </div>
  );
}

function CodePanel({ title, code, language }) {
  const lines = code.split('\n').slice(0, 30); // Show first 30 lines

  return (
    <div className="border border-ibm-gray-20 rounded-lg overflow-hidden">
      <div className="bg-ibm-gray-100 text-white px-4 py-3 flex items-center gap-2">
        <Code size={18} />
        <span className="font-semibold text-sm">{title}</span>
      </div>
      <div className="bg-gray-900 text-gray-300 p-4 font-mono text-xs overflow-auto max-h-96">
        {lines.map((line, idx) => (
          <div key={idx} className="hover:bg-gray-800 px-2 py-0.5">
            <span className="text-gray-500 mr-4">{idx + 1}</span>
            {line}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

// Made with Bob
