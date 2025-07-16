import React, { createContext, useContext, useState } from 'react';

const AnimationContext = createContext<{ enabled: boolean; toggle: () => void }>({
  enabled: true,
  toggle: () => {},
});

export const useAnimation = () => useContext(AnimationContext);

export const AnimationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [enabled, setEnabled] = useState(() => {
    const stored = localStorage.getItem('animationsEnabled');
    return stored === null ? true : stored === 'true';
  });

  const toggle = () => {
    setEnabled((prev) => {
      localStorage.setItem('animationsEnabled', String(!prev));
      return !prev;
    });
  };

  return (
    <AnimationContext.Provider value={{ enabled, toggle }}>
      {children}
    </AnimationContext.Provider>
  );
}; 