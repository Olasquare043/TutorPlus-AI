import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { AuthLayout } from '../components/auth/AuthLayout';
import { tutorAPI } from '../api/endpoints';
import { Send, Mic, Volume2, Loader } from 'lucide-react';

export default function TutorPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [subject, setSubject] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage = { role: 'user', content: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await tutorAPI.askQuestion({
        query: input,
        subject: subject || null,
        language,
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response_text,
        audioUrl: response.data.response_audio_url,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayAudio = (audioUrl) => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.play();
      setSpeaking(true);
      audio.onended = () => setSpeaking(false);
    }
  };

  return (
    <AuthLayout title="Tutor Chat">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Sidebar */}
        <div className="lg:col-span-1">
          <div className="card space-y-4">
            <h3 className="font-bold text-gray-900">Settings</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Subject (Optional)
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="e.g., Biology"
                className="input-field text-sm"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="input-field text-sm"
              >
                <option value="en">English</option>
                <option value="yo">Yoruba</option>
                <option value="ha">Hausa</option>
                <option value="ig">Igbo</option>
              </select>
            </div>

            <div className="text-xs text-gray-500 p-3 bg-gray-50 rounded">
              💡 Tip: The AI will use your curriculum documents to provide accurate answers.
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-3">
          <div className="card flex flex-col h-screen lg:h-[600px]">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto mb-4 space-y-4">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <Brain size={48} className="mx-auto mb-4 text-gray-300" />
                    <p>No messages yet. Ask me something!</p>
                  </div>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <p className="text-sm">{msg.content}</p>
                      {msg.audioUrl && (
                        <button
                          onClick={() => handlePlayAudio(msg.audioUrl)}
                          className="mt-2 flex items-center gap-2 text-xs hover:opacity-80"
                        >
                          <Volume2 size={14} />
                          {speaking ? 'Playing...' : 'Play Audio'}
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg flex items-center gap-2">
                    <Loader size={16} className="animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Form */}
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question..."
                className="input-field flex-1"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="btn-primary disabled:opacity-50"
              >
                <Send size={20} />
              </button>
              <button
                type="button"
                className="btn-secondary"
                title="Voice input (coming soon)"
              >
                <Mic size={20} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
