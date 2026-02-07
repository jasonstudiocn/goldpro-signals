import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, TrendingUp, Brain, History, Settings as SettingsIcon } from 'lucide-react';

const Layout = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: '仪表盘', icon: LayoutDashboard },
    { path: '/technical', label: '技术分析', icon: TrendingUp },
    { path: '/ai-analysis', label: 'AI分析', icon: Brain },
    { path: '/signals', label: '信号历史', icon: History },
    { path: '/settings', label: '设置', icon: SettingsIcon },
  ];

  return (
    <div className="flex h-screen bg-[#0A0A0A]">
      {/* 侧边栏 */}
      <aside className="w-64 border-r border-white/10 bg-[#0A0A0A]" data-testid="sidebar">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-gradient-to-br from-[#D4AF37] to-[#AA8C2C] rounded-sm flex items-center justify-center">
              <span className="text-black font-bold text-xl">G</span>
            </div>
            <div>
              <h1 className="text-xl font-heading font-bold text-white">黄金交易</h1>
              <p className="text-xs text-gray-400">分析系统</p>
            </div>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`nav-${item.label}`}
                  className={`nav-link flex items-center gap-3 px-4 py-3 rounded-sm text-sm font-medium ${
                    isActive
                      ? 'active text-[#D4AF37] bg-white/5 border-l-2 border-[#D4AF37]'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-white/10">
          <div className="text-xs text-gray-500">
            <p>实时数据分析</p>
            <p className="mt-1">Powered by AI</p>
          </div>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 overflow-auto" data-testid="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;