import client from './client';

// Auth endpoints
export const authAPI = {
  register: (data) => client.post('/auth/register', data),
  login: (data) => client.post('/auth/login', data),
  logout: () => client.post('/auth/logout'),
  getCurrentUser: () => client.get('/auth/me'),
  refreshToken: (refreshToken) =>
    client.post('/auth/refresh', { refresh_token: refreshToken }),
};

// Tutor endpoints
export const tutorAPI = {
  askQuestion: (data) => client.post('/tutor/ask', data),
  generateMCQ: (data) => client.post('/tutor/generate-mcq', data),
  generateVoice: (data) => client.post('/tutor/generate-voice', data),
  processVoiceQuery: (audioFile, language = 'en') => {
    const formData = new FormData();
    formData.append('file', audioFile);
    formData.append('language', language);
    return client.post('/tutor/process-voice-query', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// Progress endpoints
export const progressAPI = {
  getUserProgress: () => client.get('/progress/my'),
  trackProgress: (data) => client.post('/progress/track', data),
  getStudentProgress: (subject) => client.get(`/progress/student/${subject}`),
  updateStudentProgress: (subject, data) =>
    client.put(`/progress/student/${subject}`, data),
};

// MCQ endpoints
export const mcqAPI = {
  getMCQ: (id) => client.get(`/mcq/${id}`),
  getMCQBySubject: (subject, topic, limit) =>
    client.get(`/mcq/subject/${subject}`, { params: { topic, limit } }),
  submitMCQAttempt: (data) => client.post('/mcq/attempt', data),
  getUserAttempts: () => client.get('/mcq/attempts/my'),
};

// Admin endpoints
export const adminAPI = {
  uploadCurriculum: (file, subject, gradeLevel, examBoard = 'WAEC') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subject', subject);
    formData.append('grade_level', gradeLevel);
    formData.append('exam_board', examBoard);
    return client.post('/admin/upload-curriculum', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getCurriculumStats: () => client.get('/admin/curriculum-stats'),
};