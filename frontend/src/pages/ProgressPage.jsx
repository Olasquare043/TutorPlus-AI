import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { AuthLayout } from '../components/auth/AuthLayout';
import { progressAPI } from '../api/endpoints';
import { BarChart3, TrendingUp, Award, Loader, AlertCircle } from 'lucide-react';

export default function ProgressPage() {
  const { user } = useAuth();
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSubject, setSelectedSubject] = useState(null);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      setLoading(true);
      const response = await progressAPI.getUserProgress();
      setProgress(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch progress');
    } finally {
      setLoading(false);
    }
  };

  const subjects = [
    'Mathematics',
    'Biology',
    'Chemistry',
    'Physics',
    'English',
    'History',
    'Geography',
    'Literature',
  ];

  const getProgressPercentage = (completed, total) => {
    if (total === 0) return 0;
    return Math.round((completed / total) * 100);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <AuthLayout title="Progress Tracker">
        <div className="flex items-center justify-center min-h-96">
          <Loader size={40} className="animate-spin text-blue-600" />
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout title="Progress Tracker">
      <div className="space-y-6">
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Lessons</p>
                <p className="text-3xl font-bold text-blue-600">
                  {progress.reduce((sum, p) => sum + p.lessons_completed, 0)}
                </p>
              </div>
              <TrendingUp size={40} className="text-blue-200" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Subjects</p>
                <p className="text-3xl font-bold text-purple-600">
                  {new Set(progress.map(p => p.subject)).size}
                </p>
              </div>
              <Award size={40} className="text-purple-200" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Average Score</p>
                <p className="text-3xl font-bold text-green-600">
                  {progress.length > 0
                    ? Math.round(progress.reduce((sum, p) => sum + p.quiz_score, 0) / progress.length)
                    : 0}%
                </p>
              </div>
              <BarChart3 size={40} className="text-green-200" />
            </div>
          </div>
        </div>

        {/* Subject Selection */}
        <div className="card">
          <h3 className="font-bold text-gray-900 mb-4">Subjects</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {subjects.map((subject) => (
              <button
                key={subject}
                onClick={() => setSelectedSubject(selectedSubject === subject ? null : subject)}
                className={`py-3 px-4 rounded-lg font-medium transition-colors ${
                  selectedSubject === subject
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                }`}
              >
                {subject}
              </button>
            ))}
          </div>
        </div>

        {/* Progress Details */}
        {progress.length > 0 ? (
          <div className="space-y-4">
            {progress
              .filter(p => !selectedSubject || p.subject === selectedSubject)
              .map((item, idx) => (
                <div key={idx} className="card">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="font-bold text-gray-900">{item.subject}</h4>
                      <p className="text-sm text-gray-600">{item.topic}</p>
                    </div>
                    <div className={`text-2xl font-bold ${getScoreColor(item.quiz_score)}`}>
                      {item.quiz_score}%
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${getProgressPercentage(item.lessons_completed, item.total_lessons)}%`,
                      }}
                    />
                  </div>

                  <p className="text-xs text-gray-600 mt-2">
                    {item.lessons_completed} of {item.total_lessons} lessons completed
                  </p>
                </div>
              ))}
          </div>
        ) : (
          <div className="card text-center py-12 text-gray-500">
            <BarChart3 size={48} className="mx-auto mb-4 text-gray-300" />
            <p>No progress data yet. Start learning to see your progress!</p>
          </div>
        )}
      </div>
    </AuthLayout>
  );
}