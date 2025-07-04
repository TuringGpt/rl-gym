import { useSession } from '../../contexts/SessionContext';
import { useTheme } from '../../contexts/ThemeContext';

const Header = () => {
  const { currentSession } = useSession();
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4 dark:bg-gray-800 dark:border-gray-600">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
            SP-API Testing Dashboard
          </h1>
        </div>

        <div className="flex items-center space-x-4">
          {currentSession ? (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-300">Session:</span>
              <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded text-sm font-mono dark:bg-blue-900/30 dark:text-blue-200 dark:border dark:border-blue-400">
                {currentSession}
              </span>
              <div className="w-2 h-2 bg-success-500 rounded-full dark:bg-green-500" title="Connected"></div>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-300">No active session</span>
              <div className="w-2 h-2 bg-error-500 rounded-full dark:bg-red-500" title="Not connected"></div>
            </div>
          )}

          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 transition-colors duration-200"
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            <span className="text-lg">
              {theme === 'light' ? '🌙' : '☀️'}
            </span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;