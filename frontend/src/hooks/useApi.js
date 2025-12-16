import { useState } from 'react';

export function useApi(apiCall) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = async (...args) => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiCall(...args);
      setData(result.data);
      return result.data;
    } catch (err) {
      const message = err.response?.data?.detail || err.message;
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, execute };
}