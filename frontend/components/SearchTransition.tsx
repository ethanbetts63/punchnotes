"use client";

import { createContext, useContext, useTransition, type ReactNode } from "react";

type SearchTransitionContextValue = {
  isPending: boolean;
  navigate: (run: () => void) => void;
};

const SearchTransitionContext = createContext<SearchTransitionContextValue | null>(null);

export function SearchTransitionProvider({ children }: { children: ReactNode }) {
  const [isPending, startTransition] = useTransition();

  return (
    <SearchTransitionContext.Provider value={{ isPending, navigate: startTransition }}>
      {children}
    </SearchTransitionContext.Provider>
  );
}

export function useSearchTransition(): SearchTransitionContextValue {
  const ctx = useContext(SearchTransitionContext);
  if (ctx) return ctx;
  // No provider above (e.g. browse pages navigating to a different route) - navigate immediately.
  return { isPending: false, navigate: (run) => run() };
}
