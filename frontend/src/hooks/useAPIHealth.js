import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { checkAPIHealth } from '../services/api';

export const useAPIHealth = () => {
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const { data, error, isLoading: queryLoading } = useQuery(
    'apiHealth',
    checkAPIHealth,
    {
      retry: 3,
      retryDelay: 2000,
      refetchInterval: 30000, // Check every 30 seconds
      refetchIntervalInBackground: true,
      onSuccess: () => {
        setIsHealthy(true);
        setIsLoading(false);
      },
      onError: () => {
        setIsHealthy(false);
        setIsLoading(false);
      },
    }
  );

  useEffect(() => {
    if (queryLoading) {
      setIsLoading(true);
    } else {
      setIsLoading(false);
    }
  }, [queryLoading]);

  return {
    isHealthy,
    isLoading,
    error,
    data,
  };
};
