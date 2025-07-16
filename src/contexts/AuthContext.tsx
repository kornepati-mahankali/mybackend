import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { apiService } from '../services/api';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, username: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing auth token on app load
    const token = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('currentUser');
    
    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      // Super Admin credentials
      if (email === 'super@scraper.com' && password === 'SuperScraper2024!') {
        const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const superAdminUser: User = {
          id: 'super-admin-1',
          email: storedUser.email || 'super@scraper.com',
          username: storedUser.username || 'Super Admin',
          role: 'super_admin',
          createdAt: storedUser.createdAt || new Date().toISOString(),
          lastLogin: new Date().toISOString(),
          isActive: true,
          bio: storedUser.bio || '',
        };
        setUser(superAdminUser);
        localStorage.setItem('currentUser', JSON.stringify(superAdminUser));
        localStorage.setItem('authToken', 'demo-super-admin-token');
        return true;
      }

      // Regular Admin credentials
      if (email === 'admin@scraper.com' && password === 'admin123') {
        const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
        const adminUser: User = {
          id: 'admin-1',
          email: storedUser.email || 'admin@scraper.com',
          username: storedUser.username || 'Admin',
          role: 'admin',
          createdAt: storedUser.createdAt || new Date().toISOString(),
          lastLogin: new Date().toISOString(),
          isActive: true,
          bio: storedUser.bio || '',
        };
        setUser(adminUser);
        localStorage.setItem('currentUser', JSON.stringify(adminUser));
        localStorage.setItem('authToken', 'demo-admin-token');
        return true;
      }

      // Try backend authentication
      try {
        const response = await apiService.login(email, password);
        setUser(response.user);
        localStorage.setItem('currentUser', JSON.stringify(response.user));
        localStorage.setItem('authToken', response.token);
        return true;
      } catch (backendError) {
        console.warn('Backend login failed, falling back to local auth:', backendError);
        
        // Fallback to local storage for demo
        const users = JSON.parse(localStorage.getItem('users') || '[]');
        const foundUser = users.find((u: User & { password: string }) => 
          u.email === email && u.password === password
        );

        if (foundUser) {
          const { password: _, ...userWithoutPassword } = foundUser;
          setUser(userWithoutPassword);
          localStorage.setItem('currentUser', JSON.stringify(userWithoutPassword));
          localStorage.setItem('authToken', `local-token-${foundUser.id}`);
          return true;
        }
      }
      
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (email: string, username: string, password: string): Promise<boolean> => {
    try {
      // Try backend registration
      try {
        const response = await apiService.register(email, username, password);
        setUser(response.user);
        localStorage.setItem('currentUser', JSON.stringify(response.user));
        localStorage.setItem('authToken', response.token);
        return true;
      } catch (backendError) {
        console.warn('Backend registration failed, falling back to local auth:', backendError);
        
        // Fallback to local storage for demo
        const users = JSON.parse(localStorage.getItem('users') || '[]');
        
        if (users.some((u: User) => u.email === email)) {
          return false;
        }

        const newUser: User & { password: string } = {
          id: Date.now().toString(),
          email,
          username,
          password,
          role: 'user',
          createdAt: new Date().toISOString(),
          isActive: true,
        };

        users.push(newUser);
        localStorage.setItem('users', JSON.stringify(users));

        const { password: _, ...userWithoutPassword } = newUser;
        setUser(userWithoutPassword);
        localStorage.setItem('currentUser', JSON.stringify(userWithoutPassword));
        localStorage.setItem('authToken', `local-token-${newUser.id}`);
        return true;
      }
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      await apiService.logout();
    } catch (error) {
      console.warn('Backend logout failed:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('currentUser');
      localStorage.removeItem('authToken');
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};