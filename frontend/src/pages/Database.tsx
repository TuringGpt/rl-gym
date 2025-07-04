import { useState, useEffect } from 'react';
import { useSession } from '../contexts/SessionContext';
import { sessionService } from '../services/sessionService';
import { DatabaseState } from '../types/api';

const Database = () => {
  const { currentSession } = useSession();
  const [dbState, setDbState] = useState<DatabaseState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (currentSession) {
      loadDatabaseState();
    }
  }, [currentSession]);

  const loadDatabaseState = async () => {
    if (!currentSession) return;

    try {
      setLoading(true);
      setError(null);
      const state = await sessionService.getDatabaseState();
      setDbState(state);
    } catch (err: any) {
      setError(err.message || 'Failed to load database state');
    } finally {
      setLoading(false);
    }
  };

  const refreshState = async () => {
    setRefreshing(true);
    await loadDatabaseState();
    setRefreshing(false);
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatNumber = (num: number): string => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  if (!currentSession) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Database State</h1>
        <div className="card bg-warning-50 border-warning-200">
          <div className="text-center py-8">
            <div className="text-warning-500 text-4xl mb-4">⚠️</div>
            <h3 className="text-lg font-medium text-warning-800 mb-2">No Active Session</h3>
            <p className="text-warning-600 mb-4">
              You need an active session to view database state. Please create or select a session from the Dashboard.
            </p>
            <a href="/" className="btn-primary">
              Go to Dashboard
            </a>
          </div>
        </div>
      </div>
    );
  }

  if (loading && !dbState) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Database State</h1>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading database state...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Database State</h1>
        <div className="card">
          <div className="text-center py-8">
            <div className="text-error-500 text-4xl mb-4">⚠️</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to Load Database State</h3>
            <p className="text-gray-600 mb-4">{error}</p>
            <button onClick={loadDatabaseState} className="btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Database State</h1>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Session:</span>
            <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded text-sm font-mono">
              {currentSession}
            </span>
          </div>
          <button
            onClick={refreshState}
            disabled={refreshing}
            className="btn-secondary"
          >
            {refreshing ? '🔄 Refreshing...' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      {dbState && (
        <>
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="card text-center">
              <div className="text-3xl font-bold text-primary-900 mb-2">
                {formatNumber(dbState.total_listings)}
              </div>
              <div className="text-sm text-gray-600">Total Listings</div>
            </div>

            <div className="card text-center">
              <div className="text-3xl font-bold text-success-900 mb-2">
                {formatNumber(dbState.active_listings)}
              </div>
              <div className="text-sm text-gray-600">Active Listings</div>
            </div>

            <div className="card text-center">
              <div className="text-3xl font-bold text-error-900 mb-2">
                {formatNumber(dbState.inactive_listings)}
              </div>
              <div className="text-sm text-gray-600">Inactive Listings</div>
            </div>

            <div className="card text-center">
              <div className="text-3xl font-bold text-warning-900 mb-2">
                {formatNumber(Object.keys(dbState.seller_counts || {}).length)}
              </div>
              <div className="text-sm text-gray-600">Total Sellers</div>
            </div>
          </div>

          {/* Price Statistics */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Price Statistics</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-900 mb-1">
                  {formatCurrency(dbState.price_stats.min_price)}
                </div>
                <div className="text-sm text-blue-600">Minimum Price</div>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-900 mb-1">
                  {formatCurrency(dbState.price_stats.avg_price)}
                </div>
                <div className="text-sm text-green-600">Average Price</div>
              </div>

              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-900 mb-1">
                  {formatCurrency(dbState.price_stats.max_price)}
                </div>
                <div className="text-sm text-purple-600">Maximum Price</div>
              </div>
            </div>
          </div>

          {/* Inventory Summary */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Inventory Summary</h2>
            <div className="text-center p-6 bg-indigo-50 rounded-lg">
              <div className="text-4xl font-bold text-indigo-900 mb-2">
                {formatNumber(dbState.total_inventory)}
              </div>
              <div className="text-lg text-indigo-600">Total Units in Stock</div>
            </div>
          </div>

          {/* Seller Breakdown */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Seller Breakdown</h2>
            <div className="space-y-3">
              {Object.entries(dbState.seller_counts || {}).map(([sellerId, sellerData]) => (
                <div key={sellerId} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="font-medium text-gray-900">{sellerData.name}</div>
                    <div className="text-sm text-gray-600">ID: {sellerId}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-semibold text-gray-900">
                      {formatNumber(sellerData.count)}
                    </div>
                    <div className="text-sm text-gray-600">listings</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Status Distribution */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Status Distribution</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-700">Active Listings</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-success-500 h-2 rounded-full"
                      style={{
                        width: `${(dbState.active_listings / dbState.total_listings) * 100}%`
                      }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">
                    {Math.round((dbState.active_listings / dbState.total_listings) * 100)}%
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-gray-700">Inactive Listings</span>
                <div className="flex items-center space-x-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-error-500 h-2 rounded-full"
                      style={{
                        width: `${(dbState.inactive_listings / dbState.total_listings) * 100}%`
                      }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">
                    {Math.round((dbState.inactive_listings / dbState.total_listings) * 100)}%
                  </span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Database;