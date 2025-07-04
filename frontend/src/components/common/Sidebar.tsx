import { Link, useLocation } from 'react-router-dom';

const navigation = [
  { name: 'Dashboard', href: '/', icon: '🏠' },
  { name: 'Test Flows', href: '/flows', icon: '🔄' },
  { name: 'Validation', href: '/validation', icon: '✅' },
  { name: 'Database', href: '/database', icon: '🗄️' },
  { name: 'Tools', href: '/tools', icon: '🛠️' },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg border-r border-gray-200 dark:bg-gray-800 dark:border-gray-600">
      <div className="flex flex-col h-full">
        <div className="flex-1 flex flex-col pt-6 pb-4 overflow-y-auto">
          <nav className="mt-5 flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`
                    group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-200
                    ${isActive
                      ? 'bg-primary-100 text-primary-900 border-r-2 border-primary-500 dark:bg-blue-900/30 dark:text-blue-200 dark:border-blue-400'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-gray-100'
                    }
                  `}
                >
                  <span className="mr-3 text-lg">{item.icon}</span>
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex-shrink-0 flex border-t border-gray-200 p-4 dark:border-gray-600">
          <div className="flex items-center">
            <div className="ml-3">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                SP-API Testing Dashboard v1.0
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;