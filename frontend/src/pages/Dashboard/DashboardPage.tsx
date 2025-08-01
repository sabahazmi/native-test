import React from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';

const DashboardPage: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.auth);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back, {user?.first_name}!</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Total Balance</h3>
          <p className="text-2xl font-bold text-gray-900">$12,450.00</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">This Month</h3>
          <p className="text-2xl font-bold text-green-600">+$1,250.00</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Transactions</h3>
          <p className="text-2xl font-bold text-gray-900">24</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Pending</h3>
          <p className="text-2xl font-bold text-yellow-600">2</p>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between py-3 border-b border-gray-200">
            <div>
              <p className="font-medium text-gray-900">Transfer to John Doe</p>
              <p className="text-sm text-gray-500">Today, 2:30 PM</p>
            </div>
            <span className="text-red-600 font-medium">-$250.00</span>
          </div>
          <div className="flex items-center justify-between py-3 border-b border-gray-200">
            <div>
              <p className="font-medium text-gray-900">Salary Deposit</p>
              <p className="text-sm text-gray-500">Yesterday, 9:00 AM</p>
            </div>
            <span className="text-green-600 font-medium">+$3,500.00</span>
          </div>
          <div className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium text-gray-900">Coffee Shop</p>
              <p className="text-sm text-gray-500">Dec 15, 8:45 AM</p>
            </div>
            <span className="text-red-600 font-medium">-$4.50</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;