"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { getErrorMessage } from "@/lib/api/client";

interface AsyncOptions {
  pollMs?: number;
}

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

export function useAsync<T>(
  fetcher: () => Promise<T>,
  deps: ReadonlyArray<unknown>,
  options: AsyncOptions = {},
): AsyncState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadedKey, setLoadedKey] = useState<string | null>(null);
  const [loadedTick, setLoadedTick] = useState(-1);
  const [tick, setTick] = useState(0);

  const fetcherRef = useRef(fetcher);
  useEffect(() => {
    fetcherRef.current = fetcher;
  });

  const depsKey = JSON.stringify(deps);
  const loading = loadedKey !== depsKey || loadedTick !== tick;

  useEffect(() => {
    const requestedTick = tick;
    let cancelled = false;

    (async () => {
      try {
        const result = await fetcherRef.current();
        if (cancelled) return;
        setData(result);
        setError(null);
      } catch (err) {
        if (cancelled) return;
        setError(getErrorMessage(err));
      } finally {
        if (!cancelled) {
          setLoadedKey(depsKey);
          setLoadedTick(requestedTick);
        }
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [depsKey, tick]);

  useEffect(() => {
    if (!options.pollMs) return;
    const timer = setInterval(() => setTick((value) => value + 1), options.pollMs);
    return () => clearInterval(timer);
  }, [options.pollMs]);

  const reload = useCallback(() => setTick((value) => value + 1), []);

  return { data, loading, error, reload };
}
