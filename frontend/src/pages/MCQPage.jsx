import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { AuthLayout } from '../components/auth/AuthLayout';
import { tutorAPI, mcqAPI } from '../api/endpoints';
import { BookOpen, Zap, CheckCircle, XCircle, Loader } from 'lucide-react';

export default function MCQPage() {
  const { user } = useAuth();
  const [mode, setMode] = useState('generate'); // 'generate' or 'solve'
  const [subject, setSubject] = useState('');
  const [topic, setTopic] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('medium');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState('');
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const handleGenerateMCQ = async (e) => {
    e.preventDefault();
    if (!subject || !topic) {
      alert('Please fill in subject and topic');
      return;
    }

    setLoading(true);
    try {
      const response = await tutorAPI.generateMCQ({
        subject,
        topic,
        number_of_questions: numQuestions,
        difficulty,
        language,
      });

      setQuestions(response.data.questions);
      setAnswers({});
      setSubmitted(false);
    } catch (error) {
      alert('Failed to generate MCQ. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionIndex, selectedOption) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: selectedOption,
    }));
  };

  const handleSubmitAnswers = async () => {
    if (Object.keys(answers).length === 0) {
      alert('Please answer at least one question');
      return;
    }

    setSubmitted(true);
    // In a real app, you'd submit to backend for grading
  };

  return (
    <AuthLayout title="MCQ Practice">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Mode Selector */}
        <div className="flex gap-4">
          <button
            onClick={() => setMode('generate')}
            className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
              mode === 'generate'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            <Zap className="inline mr-2" size={20} />
            Generate MCQ
          </button>
          <button
            onClick={() => setMode('solve')}
            className={`flex-1 py-3 rounded-lg font-medium transition-colors ${
              mode === 'solve'
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            <BookOpen className="inline mr-2" size={20} />
            Solve Questions
          </button>
        </div>

        {/* Generate MCQ Form */}
        {mode === 'generate' && (
          <div className="card space-y-4">
            <h3 className="text-lg font-bold text-gray-900">Generate Questions</h3>
            
            <form onSubmit={handleGenerateMCQ} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject *
                  </label>
                  <input
                    type="text"
                    value={subject}
                    onChange={(e) => setSubject(e.target.value)}
                    placeholder="e.g., Biology"
                    className="input-field"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Topic *
                  </label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., Photosynthesis"
                    className="input-field"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Number of Questions
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    value={numQuestions}
                    onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Difficulty
                  </label>
                  <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="input-field">
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Language
                  </label>
                  <select value={language} onChange={(e) => setLanguage(e.target.value)} className="input-field">
                    <option value="en">English</option>
                    <option value="yo">Yoruba</option>
                    <option value="ha">Hausa</option>
                    <option value="ig">Igbo</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading && <Loader size={20} className="animate-spin" />}
                {loading ? 'Generating...' : 'Generate Questions'}
              </button>
            </form>
          </div>
        )}

        {/* MCQ Display */}
        {questions && (
          <div className="space-y-4">
            <div className="card">
              <h3 className="font-bold text-gray-900 mb-4">
                {subject} - {topic}
              </h3>
              
              <div className="space-y-6 max-h-96 overflow-y-auto">
                {questions.split('\n\n').map((question, idx) => {
                  if (!question.trim().startsWith('Q')) return null;
                  
                  return (
                    <div key={idx} className="border-b pb-4 last:border-b-0">
                      <p className="font-medium text-gray-900 mb-3">{question.split('\n')[0]}</p>
                      
                      <div className="space-y-2">
                        {['A', 'B', 'C', 'D'].map((option) => (
                          <label key={option} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                            <input
                              type="radio"
                              name={`question-${idx}`}
                              value={option}
                              checked={answers[idx] === option}
                              onChange={() => handleAnswerChange(idx, option)}
                              className="mr-3"
                            />
                            <span className="text-gray-700">{option})</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>

              <button
                onClick={handleSubmitAnswers}
                disabled={submitted}
                className="w-full mt-6 btn-primary disabled:opacity-50"
              >
                {submitted ? '✓ Submitted' : 'Submit Answers'}
              </button>

              {submitted && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800 font-medium">
                    ✓ Your answers have been recorded!
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {!questions && mode === 'generate' && (
          <div className="card text-center py-12 text-gray-500">
            <BookOpen size={48} className="mx-auto mb-4 text-gray-300" />
            <p>Generate questions to get started</p>
          </div>
        )}
      </div>
    </AuthLayout>
  );
}
