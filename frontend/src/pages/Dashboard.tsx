import { useState, useEffect } from 'react';
import { useSession } from '../contexts/SessionContext';
import { sessionService } from '../services/sessionService';

const Dashboard = () => {
  const { currentSession, createSession, isLoading, error, setCurrentSession } = useSession();
  const [sessionInput, setSessionInput] = useState('');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [dbState, setDbState] = useState<any>(null);

  // Check backend status on mount
  useEffect(() => {
    checkBackendStatus();
  }, []);

  // Load database state when session changes
  useEffect(() => {
    if (currentSession) {
      loadDatabaseState();
    }
  }, [currentSession]);

  const checkBackendStatus = async () => {
    try {
      await sessionService.healthCheck();
      setBackendStatus('online');
    } catch (error) {
      setBackendStatus('offline');
    }
  };

  const loadDatabaseState = async () => {
    if (!currentSession) return;

    try {
      const state = await sessionService.getDatabaseState();
      setDbState(state);
    } catch (error) {
      console.error('Failed to load database state:', error);
    }
  };

  const handleCreateSession = async () => {
    try {
      await createSession();
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  };

  const handleSessionInput = (e: React.FormEvent) => {
    e.preventDefault();
    if (sessionInput.trim()) {
      // Basic validation for session ID format
      if (sessionInput.match(/^session_[a-f0-9]{12}$/)) {
        // Set the session (this will be validated by the backend on first request)
        setCurrentSession(sessionInput.trim());
        setSessionInput('');
      } else {
        alert('Invalid session ID format. Expected format: session_xxxxxxxxxxxx');
      }
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${backendStatus === 'online' ? 'bg-success-500' :
            backendStatus === 'offline' ? 'bg-error-500' : 'bg-warning-500'
            }`}></div>
          <span className="text-sm text-gray-600">
            Backend: {backendStatus === 'checking' ? 'Checking...' : backendStatus}
          </span>
        </div>
      </div>

      {/* Session Management */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Session Management</h2>

          {currentSession ? (
            <div className="space-y-4">
              <div className="p-4 bg-success-50 border border-success-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-success-800">Active Session</p>
                    <p className="text-lg font-mono text-success-900">{currentSession}</p>
                  </div>
                  <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                </div>
              </div>

              <button
                onClick={() => setCurrentSession(null)}
                className="btn-secondary w-full"
              >
                Clear Session
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-4 bg-warning-50 border border-warning-200 rounded-lg">
                <p className="text-sm text-warning-800">No active session</p>
                <p className="text-xs text-warning-600 mt-1">
                  Create a new session or input an existing session ID to get started
                </p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={handleCreateSession}
                  disabled={isLoading}
                  className="btn-primary w-full"
                >
                  {isLoading ? 'Creating...' : 'Create New Session'}
                </button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">or</span>
                  </div>
                </div>

                <form onSubmit={handleSessionInput} className="space-y-2">
                  <input
                    type="text"
                    value={sessionInput}
                    onChange={(e) => setSessionInput(e.target.value)}
                    placeholder="Enter existing session ID (e.g., session_abc123def456)"
                    className="input"
                  />
                  <button type="submit" className="btn-secondary w-full">
                    Use Session
                  </button>
                </form>
              </div>
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-error-50 border border-error-200 rounded-lg">
              <p className="text-sm text-error-800">{error}</p>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Stats</h2>

          {currentSession && dbState ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-primary-50 rounded-lg">
                  <div className="text-2xl font-bold text-primary-900">{dbState.total_listings}</div>
                  <div className="text-sm text-primary-600">Total Listings</div>
                </div>
                <div className="text-center p-3 bg-success-50 rounded-lg">
                  <div className="text-2xl font-bold text-success-900">{dbState.active_listings}</div>
                  <div className="text-sm text-success-600">Active</div>
                </div>
                <div className="text-center p-3 bg-error-50 rounded-lg">
                  <div className="text-2xl font-bold text-error-900">{dbState.inactive_listings}</div>
                  <div className="text-sm text-error-600">Inactive</div>
                </div>
                <div className="text-center p-3 bg-warning-50 rounded-lg">
                  <div className="text-2xl font-bold text-warning-900">{Object.keys(dbState.seller_counts || {}).length}</div>
                  <div className="text-sm text-warning-600">Sellers</div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Avg Price:</span>
                  <span className="font-medium">${dbState.price_stats?.avg_price?.toFixed(2) || '0.00'}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total Inventory:</span>
                  <span className="font-medium">{dbState.total_inventory?.toLocaleString() || '0'}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>Create or select a session to view statistics</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <a
            href="/flows"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
          >
            <div className="text-2xl mb-2">🔄</div>
            <div className="font-medium text-gray-900">View Test Flows</div>
            <div className="text-sm text-gray-600">Browse available test scenarios</div>
          </a>

          <a
            href="/validation"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
          >
            <div className="text-2xl mb-2">✅</div>
            <div className="font-medium text-gray-900">Run Validation</div>
            <div className="text-sm text-gray-600">Validate test flow results</div>
          </a>

          <a
            href="/database"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
          >
            <div className="text-2xl mb-2">🗄️</div>
            <div className="font-medium text-gray-900">Database State</div>
            <div className="text-sm text-gray-600">View current data state</div>
          </a>

          <a
            href="/tools"
            className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-center"
          >
            <div className="text-2xl mb-2">🛠️</div>
            <div className="font-medium text-gray-900">Tools</div>
            <div className="text-sm text-gray-600">Reset database & utilities</div>
          </a>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;