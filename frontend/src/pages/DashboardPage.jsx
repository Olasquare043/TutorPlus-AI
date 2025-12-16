import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { AuthLayout } from '../components/auth/AuthLayout';
import { BookOpen, Brain, BarChart3, Mic, Link as LinkIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const features = [
    {
      icon: Brain,
      title: 'Tutor Chat',
      description: 'Ask questions and get AI-powered answers',
      color: 'bg-blue-100',
      iconColor: 'text-blue-600',
      action: () => navigate('/tutor'),
    },
    {
      icon: BookOpen,
      title: 'MCQ Practice',
      description: 'Generate and solve multiple choice questions',
      color: 'bg-purple-100',
      iconColor: 'text-purple-600',
      action: () => navigate('/mcq'),
    },
    {
      icon: BarChart3,
      title: 'Progress Tracker',
      description: 'Track your learning progress by subject',
      color: 'bg-green-100',
      iconColor: 'text-green-600',
      action: () => navigate('/progress'),
    },
    {
      icon: Mic,
      title: 'Voice Chat',
      description: 'Ask questions using voice input',
      color: 'bg-orange-100',
      iconColor: 'text-orange-600',
      action: () => navigate('/tutor?voice=true'),
    },
  ];

  return (
    <AuthLayout title="Dashboard">
      <div className="space-y-8">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 text-white">
          <h2 className="text-3xl font-bold">Welcome back, {user?.full_name || user?.username}! 👋</h2>
          <p className="mt-2 text-blue-100">
            Ready to learn? Choose a feature below to get started.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                onClick={feature.action}
                className="cursor-pointer card hover:shadow-lg transition-shadow"
              >
                <div className={`${feature.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                  <Icon className={`${feature.iconColor}`} size={24} />
                </div>
                <h3 className="text-lg font-bold text-gray-900">{feature.title}</h3>
                <p className="text-gray-600 text-sm mt-2">{feature.description}</p>
                <div className="mt-4 flex items-center text-blue-600 hover:text-blue-700 font-medium text-sm">
                  Get Started <LinkIcon size={16} className="ml-2" />
                </div>
              </div>
            );
          })}
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Stats</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">0</p>
              <p className="text-sm text-gray-600">Questions Asked</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">0</p>
              <p className="text-sm text-gray-600">MCQs Completed</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">0%</p>
              <p className="text-sm text-gray-600">Average Score</p>
            </div>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
