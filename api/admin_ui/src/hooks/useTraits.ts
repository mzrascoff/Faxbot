import { useState, useEffect, useCallback } from 'react';
import type { ProvidersInfo } from '../api/types';

interface TraitsHook {
  loading: boolean;
  error: string | null;
  active: { outbound: string; inbound: string } | null;
  registry: Record<string, { id?: string; kind?: string; traits?: Record<string, any> }> | null;
  hasTrait: (direction: 'outbound' | 'inbound', key: string) => boolean;
  traitValue: (direction: 'outbound' | 'inbound', key: string) => any;
  refresh: () => Promise<void>;
}

// Global cache to avoid multiple API calls
let globalProvidersCache: ProvidersInfo | null = null;
let globalCachePromise: Promise<ProvidersInfo> | null = null;

export function useTraits(): TraitsHook {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [providers, setProviders] = useState<ProvidersInfo | null>(globalProvidersCache);

  const fetchProviders = useCallback(async (): Promise<ProvidersInfo> => {
    // Return existing promise if one is in flight
    if (globalCachePromise) {
      return globalCachePromise;
    }

    // Return cached data if available
    if (globalProvidersCache) {
      return globalProvidersCache;
    }

    // Create new fetch promise
    globalCachePromise = (async () => {
      try {
        const response = await fetch('/admin/providers', {
          headers: {
            'X-API-Key': localStorage.getItem('faxbot_admin_key') || '',
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch providers: ${response.status}`);
        }

        const data = await response.json();
        globalProvidersCache = data;
        return data;
      } catch (err) {
        globalCachePromise = null; // Clear promise on error so we can retry
        throw err;
      } finally {
        globalCachePromise = null; // Clear promise when done
      }
    })();

    return globalCachePromise;
  }, []);

  const refresh = useCallback(async () => {
    try {
      setError(null);
      setLoading(true);
      
      // Clear cache to force fresh fetch
      globalProvidersCache = null;
      globalCachePromise = null;
      
      const data = await fetchProviders();
      setProviders(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch provider traits');
    } finally {
      setLoading(false);
    }
  }, [fetchProviders]);

  // Initial load
  useEffect(() => {
    const load = async () => {
      try {
        setError(null);
        const data = await fetchProviders();
        setProviders(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch provider traits');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, [fetchProviders]);

  const hasTrait = useCallback((direction: 'outbound' | 'inbound', key: string): boolean => {
    if (!providers?.active || !providers?.registry) return false;
    
    const activeProvider = providers.active[direction];
    if (!activeProvider) return false;
    
    const providerInfo = providers.registry[activeProvider];
    if (!providerInfo?.traits) return false;
    
    return key in providerInfo.traits;
  }, [providers]);

  const traitValue = useCallback((direction: 'outbound' | 'inbound', key: string): any => {
    if (!providers?.active || !providers?.registry) return undefined;
    
    const activeProvider = providers.active[direction];
    if (!activeProvider) return undefined;
    
    const providerInfo = providers.registry[activeProvider];
    if (!providerInfo?.traits) return undefined;
    
    return providerInfo.traits[key];
  }, [providers]);

  return {
    loading,
    error,
    active: providers?.active || null,
    registry: providers?.registry || null,
    hasTrait,
    traitValue,
    refresh,
  };
}

// Re-export provider utilities for convenience
export { getProviderDisplayName, getProviderIcon, getProviderColor, getProviderCategory } from '../utils/providerIcons';
