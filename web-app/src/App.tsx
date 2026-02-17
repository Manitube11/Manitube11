import { useEffect, useState } from 'react';
import WebApp from '@twa-dev/sdk';
import {
  Home,
  Wallet,
  ShoppingBag,
  TrendingUp,
  Send,
  Plus,
  ArrowRight,
  User,
  Crown
} from 'lucide-react';

function App() {
  const [userData, setUserData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'home' | 'store' | 'wallet'>('home');
  const [balance, setBalance] = useState(150.00);

  useEffect(() => {
    if (WebApp.initDataUnsafe.user) {
      setUserData(WebApp.initDataUnsafe.user);
    }
    WebApp.expand();
    // Use dark mode colors
    WebApp.setHeaderColor('#111827');
    WebApp.setBackgroundColor('#111827');
  }, []);

  const handleBuy = (price: number) => {
    WebApp.showConfirm(`Confirm purchase for $${price}?`, (confirmed) => {
      if (confirmed) {
        setBalance(prev => prev - price);
        WebApp.showAlert('Purchase successful!');
      }
    });
  };

  const renderHome = () => (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Header */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">Welcome back,</p>
          <h1 className="text-2xl font-bold text-white">
            {userData?.first_name || 'Business Owner'}
          </h1>
        </div>
        <div className="w-10 h-10 bg-gradient-to-tr from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
          {userData?.first_name ? userData.first_name[0] : 'U'}
        </div>
      </div>

      {/* Main Stats Card */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg transform hover:scale-[1.02] transition-transform">
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-blue-100 text-sm font-medium">Total Earnings</p>
            <h2 className="text-3xl font-bold mt-1">${balance.toFixed(2)}</h2>
          </div>
          <div className="bg-white/20 p-2 rounded-lg">
            <TrendingUp size={24} />
          </div>
        </div>
        <div className="flex gap-2 mt-4">
          <button className="flex-1 bg-white/20 hover:bg-white/30 py-2 rounded-lg text-sm font-medium transition-colors">
            Withdraw
          </button>
          <button className="flex-1 bg-white text-blue-600 hover:bg-gray-100 py-2 rounded-lg text-sm font-bold transition-colors">
            Deposit
          </button>
        </div>
      </div>

      {/* Quick Actions Grid */}
      <div>
        <h3 className="text-gray-400 font-medium mb-3">Quick Actions</h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { title: 'New Order', icon: Plus, color: 'bg-green-500/10 text-green-500' },
            { title: 'Send Money', icon: Send, color: 'bg-blue-500/10 text-blue-500' },
            { title: 'My Profile', icon: User, color: 'bg-orange-500/10 text-orange-500' },
            { title: 'Upgrade VIP', icon: Crown, color: 'bg-yellow-500/10 text-yellow-500' },
          ].map((action, idx) => (
            <button key={idx} className={`${action.color} p-4 rounded-xl flex flex-col items-center justify-center gap-2 hover:opacity-80 transition-opacity`}>
              <action.icon size={24} />
              <span className="font-medium text-sm">{action.title}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );

  const renderStore = () => (
    <div className="space-y-6 animate-fade-in">
      <h2 className="text-2xl font-bold text-white">Premium Store</h2>
      <div className="space-y-4">
        {[
          { name: 'Starter Plan', price: 9.99, features: ['Basic Support', '10GB Storage'], color: 'from-gray-700 to-gray-800' },
          { name: 'Pro Business', price: 29.99, features: ['Priority Support', '100GB Storage', 'Analytics'], color: 'from-blue-700 to-blue-900', popular: true },
          { name: 'Enterprise VIP', price: 99.99, features: ['24/7 Dedicated Agent', 'Unlimited Storage', 'API Access'], color: 'from-purple-700 to-purple-900' },
        ].map((item, idx) => (
          <div key={idx} className={`relative bg-gradient-to-br ${item.color} rounded-2xl p-6 text-white overflow-hidden shadow-lg border border-white/5`}>
            {item.popular && (
              <div className="absolute top-0 right-0 bg-yellow-500 text-black text-xs font-bold px-3 py-1 rounded-bl-lg">
                BEST VALUE
              </div>
            )}
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold">{item.name}</h3>
                <p className="text-white/60 text-sm mt-1">Unlock full potential</p>
              </div>
              <div className="text-2xl font-bold">${item.price}</div>
            </div>
            <ul className="space-y-2 mb-6">
              {item.features.map((feat, i) => (
                <li key={i} className="flex items-center text-sm text-white/80">
                  <div className="w-1.5 h-1.5 bg-white rounded-full mr-2" />
                  {feat}
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleBuy(item.price)}
              className="w-full bg-white text-gray-900 font-bold py-3 rounded-xl hover:bg-gray-100 transition-colors flex items-center justify-center gap-2"
            >
              Purchase Now <ArrowRight size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderWallet = () => (
    <div className="space-y-6 animate-fade-in text-center pt-8">
      <div className="inline-block p-4 rounded-full bg-blue-500/10 text-blue-500 mb-4">
        <Wallet size={48} />
      </div>
      <h2 className="text-gray-400 text-lg">Total Balance</h2>
      <div className="text-5xl font-bold text-white mb-8">${balance.toFixed(2)}</div>

      <div className="bg-gray-800 rounded-2xl p-4 divide-y divide-gray-700">
        {[
          { label: 'Pending Clearance', value: '$45.00' },
          { label: 'Available for Withdrawal', value: `$${(balance - 45).toFixed(2)}` },
          { label: 'Lifetime Earnings', value: '$1,245.00' },
        ].map((stat, idx) => (
          <div key={idx} className="flex justify-between py-4 first:pt-0 last:pb-0">
            <span className="text-gray-400">{stat.label}</span>
            <span className="text-white font-bold">{stat.value}</span>
          </div>
        ))}
      </div>

      <button className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-4 rounded-xl shadow-lg shadow-green-900/20 transition-all">
        Connect Wallet
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans pb-24">
      <div className="p-4 max-w-md mx-auto">
        {activeTab === 'home' && renderHome()}
        {activeTab === 'store' && renderStore()}
        {activeTab === 'wallet' && renderWallet()}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-gray-800 border-t border-gray-700 px-6 py-3 pb-6 safe-area-bottom">
        <div className="flex justify-between items-center max-w-md mx-auto">
          <button
            onClick={() => setActiveTab('home')}
            className={`flex flex-col items-center gap-1 ${activeTab === 'home' ? 'text-blue-500' : 'text-gray-400'}`}
          >
            <Home size={24} />
            <span className="text-xs font-medium">Home</span>
          </button>

          <button
            onClick={() => setActiveTab('store')}
            className={`flex flex-col items-center gap-1 ${activeTab === 'store' ? 'text-blue-500' : 'text-gray-400'}`}
          >
            <ShoppingBag size={24} />
            <span className="text-xs font-medium">Store</span>
          </button>

          <button
            onClick={() => setActiveTab('wallet')}
            className={`flex flex-col items-center gap-1 ${activeTab === 'wallet' ? 'text-blue-500' : 'text-gray-400'}`}
          >
            <Wallet size={24} />
            <span className="text-xs font-medium">Wallet</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;
