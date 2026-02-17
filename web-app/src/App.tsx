import { useEffect, useState } from 'react';
import WebApp from '@twa-dev/sdk';

function App() {
  const [userData, setUserData] = useState<any>(null);

  useEffect(() => {
    // Initialize the Web App
    if (WebApp.initDataUnsafe.user) {
      setUserData(WebApp.initDataUnsafe.user);
    }

    // Expand the app to full height
    WebApp.expand();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 text-gray-900 font-sans p-4 flex flex-col items-center justify-center">
      <div className="bg-white shadow-xl rounded-2xl p-8 max-w-sm w-full text-center transform transition-all hover:scale-105 duration-300">
        <div className="mb-6">
          <div className="w-20 h-20 bg-blue-500 rounded-full mx-auto flex items-center justify-center text-white text-3xl font-bold shadow-lg">
            {userData?.first_name ? userData.first_name[0] : 'U'}
          </div>
        </div>

        <h1 className="text-2xl font-bold mb-2 text-gray-800">
          Hello, {userData?.first_name || 'User'}!
        </h1>

        <p className="text-gray-500 mb-8">
          Welcome to your professional Telegram Mini App.
        </p>

        <div className="space-y-4">
          <button
            onClick={() => WebApp.showAlert(`Hello ${userData?.first_name || 'there'}!`)}
            className="w-full py-3 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
          >
            Show Alert
          </button>

          <button
            onClick={() => WebApp.close()}
            className="w-full py-3 px-6 bg-red-500 hover:bg-red-600 text-white font-semibold rounded-lg shadow-md transition duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50"
          >
            Close App
          </button>
        </div>
      </div>

      <footer className="mt-8 text-gray-400 text-sm">
        Built with React, Vite & Tailwind
      </footer>
    </div>
  );
}

export default App;
