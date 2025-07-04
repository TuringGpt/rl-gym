import { useSession } from '../../contexts/SessionContext';

const Header = () => {
  const { currentSession } = useSession();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900">
            SP-API Testing Dashboard
          </h1>
        </div>

        <div className="flex items-center space-x-4">
          {currentSession ? (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">Session:</span>
              <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded text-sm font-mono">
                {currentSession}
              </span>
              <div className="w-2 h-2 bg-success-500 rounded-full" title="Connected"></div>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600">No active session</span>
              <div className="w-2 h-2 bg-error-500 rounded-full" title="Not connected"></div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;