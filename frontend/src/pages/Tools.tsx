import { useState } from 'react';
import { useSession } from '../contexts/SessionContext';
import { sessionService } from '../services/sessionService';

const Tools = () => {
  const { currentSession } = useSession();
  const [resetting, setResetting] = useState(false);
  const [resetResult, setResetResult] = useState<string | null>(null);
  const [testingBackend, setTestingBackend] = useState(false);
  const [backendTestResult, setBackendTestResult] = useState<any>(null);
  const [sessionCopied, setSessionCopied] = useState(false);

  const handleResetDatabase = async () => {
    if (!currentSession) {
      alert('Please create or select a session first');
      return;
    }

    const confirmed = window.confirm(
      'Are you sure you want to reset the database? This will restore all data to the original seed state and cannot be undone.'
    );

    if (!confirmed) return;

    try {
      setResetting(true);
      setResetResult(null);
      const result = await sessionService.resetDatabase();
      setResetResult(`✅ ${result.message}`);
    } catch (err: any) {
      setResetResult(`❌ Reset failed: ${err.message || 'Unknown error'}`);
    } finally {
      setResetting(false);
    }
  };

  const testBackendConnection = async () => {
    try {
      setTestingBackend(true);
      setBackendTestResult(null);
      const result = await sessionService.healthCheck();
      setBackendTestResult({
        success: true,
        data: result,
        message: 'Backend connection successful'
      });
    } catch (err: any) {
      setBackendTestResult({
        success: false,
        data: null,
        message: err.message || 'Backend connection failed'
      });
    } finally {
      setTestingBackend(false);
    }
  };

  const exportSessionData = () => {
    const data = {
      sessionId: currentSession,
      timestamp: new Date().toISOString(),
      exportedBy: 'SP-API Testing Dashboard'
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session-${currentSession}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const copySessionId = async () => {
    if (!currentSession) return;

    try {
      await navigator.clipboard.writeText(currentSession);
      setSessionCopied(true);
      setTimeout(() => setSessionCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy session ID:', err);
      alert('Failed to copy session ID');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Tools & Utilities</h1>
        {currentSession && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600 dark:text-gray-300">Session:</span>
            <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded text-sm font-mono dark:bg-blue-900/30 dark:text-blue-200 dark:border dark:border-blue-400">
              {currentSession}
            </span>
          </div>
        )}
      </div>

      {/* Database Tools */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Database Tools</h2>

        <div className="space-y-4">
          <div className="p-4 border border-gray-200 rounded-lg dark:border-gray-600">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Reset Database</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
              Reset the current session's database to its original seed state. This will undo all changes made during testing.
            </p>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleResetDatabase}
                disabled={!currentSession || resetting}
                className={`${!currentSession ? 'btn-secondary opacity-50 cursor-not-allowed' : 'btn btn-error'}`}
              >
                {resetting ? '🔄 Resetting...' : '🗑️ Reset Database'}
              </button>

              {!currentSession && (
                <span className="text-sm text-gray-500 dark:text-gray-400">Requires active session</span>
              )}
            </div>

            {resetResult && (
              <div className={`mt-3 p-3 rounded-lg text-sm ${resetResult.startsWith('✅')
                ? 'bg-success-50 text-success-800 border border-success-200 dark:bg-green-600 dark:text-white dark:border-green-500'
                : 'bg-error-50 text-error-800 border border-error-200 dark:bg-red-600 dark:text-white dark:border-red-500'
                }`}>
                {resetResult}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Session Tools */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Session Tools</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg dark:border-gray-600">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Copy Session ID</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
              Copy the current session ID to clipboard for sharing or backup.
            </p>
            <button
              onClick={copySessionId}
              disabled={!currentSession}
              className={`btn ${!currentSession ? 'btn-secondary opacity-50 cursor-not-allowed' : 'btn-secondary'}`}
            >
              {sessionCopied ? '✅ Copied!' : '📋 Copy Session ID'}
            </button>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg dark:border-gray-600">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Export Session Data</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
              Export session information as a JSON file for record keeping.
            </p>
            <button
              onClick={exportSessionData}
              disabled={!currentSession}
              className={`btn ${!currentSession ? 'btn-secondary opacity-50 cursor-not-allowed' : 'btn-secondary'}`}
            >
              💾 Export Data
            </button>
          </div>
        </div>
      </div>

      {/* Backend Tools */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Backend Tools</h2>

        <div className="space-y-4">
          <div className="p-4 border border-gray-200 rounded-lg dark:border-gray-600">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Test Backend Connection</h3>
            <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
              Test the connection to the FastAPI backend server and check its health status.
            </p>

            <button
              onClick={testBackendConnection}
              disabled={testingBackend}
              className="btn-primary"
            >
              {testingBackend ? '🔄 Testing...' : '🔗 Test Connection'}
            </button>

            {backendTestResult && (
              <div className={`mt-3 p-3 rounded-lg text-sm ${backendTestResult.success
                ? 'bg-success-50 text-success-800 border border-success-200 dark:bg-green-600 dark:text-white dark:border-green-500'
                : 'bg-error-50 text-error-800 border border-error-200 dark:bg-red-600 dark:text-white dark:border-red-500'
                }`}>
                <div className="font-medium mb-1">
                  {backendTestResult.success ? '✅ Connection Successful' : '❌ Connection Failed'}
                </div>
                <div>{backendTestResult.message}</div>
                {backendTestResult.data && (
                  <pre className="mt-2 text-xs bg-white dark:bg-gray-800 dark:text-gray-200 p-2 rounded border dark:border-gray-600 overflow-x-auto">
                    {JSON.stringify(backendTestResult.data, null, 2)}
                  </pre>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Quick Links</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center dark:border-gray-600 dark:hover:bg-gray-700"
          >
            <div className="text-2xl mb-2">📚</div>
            <div className="font-medium text-gray-900 dark:text-gray-100">API Documentation</div>
            <div className="text-sm text-gray-600 dark:text-gray-300">FastAPI Swagger UI</div>
          </a>

          <a
            href="http://localhost:8000/redoc"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center dark:border-gray-600 dark:hover:bg-gray-700"
          >
            <div className="text-2xl mb-2">📖</div>
            <div className="font-medium text-gray-900 dark:text-gray-100">ReDoc</div>
            <div className="text-sm text-gray-600 dark:text-gray-300">Alternative API docs</div>
          </a>

          <a
            href="http://localhost:8000/test/help"
            target="_blank"
            rel="noopener noreferrer"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center dark:border-gray-600 dark:hover:bg-gray-700"
          >
            <div className="text-2xl mb-2">❓</div>
            <div className="font-medium text-gray-900 dark:text-gray-100">Testing Help</div>
            <div className="text-sm text-gray-600 dark:text-gray-300">API testing guide</div>
          </a>
        </div>
      </div>

      {/* System Information */}
      <div className="card bg-gray-50 dark:bg-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">System Information</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <div className="font-medium text-gray-700 dark:text-gray-300 mb-1">Frontend</div>
            <div className="text-gray-600 dark:text-gray-400">React + Vite + Tailwind CSS</div>
            <div className="text-gray-600 dark:text-gray-400">Running on port 3000</div>
          </div>

          <div>
            <div className="font-medium text-gray-700 dark:text-gray-300 mb-1">Backend</div>
            <div className="text-gray-600 dark:text-gray-400">FastAPI + SQLite</div>
            <div className="text-gray-600 dark:text-gray-400">Running on port 8000</div>
          </div>

          <div>
            <div className="font-medium text-gray-700 dark:text-gray-300 mb-1">Session Management</div>
            <div className="text-gray-600 dark:text-gray-400">Isolated databases per session</div>
            <div className="text-gray-600 dark:text-gray-400">Auto-generated session IDs</div>
          </div>

          <div>
            <div className="font-medium text-gray-700 dark:text-gray-300 mb-1">Testing Framework</div>
            <div className="text-gray-600 dark:text-gray-400">10 predefined test flows</div>
            <div className="text-gray-600 dark:text-gray-400">Automated validation system</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Tools;