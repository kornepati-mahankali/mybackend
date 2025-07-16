import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Bell, 
  Shield, 
  Database, 
  Palette,
  Download,
  Trash2,
  Save,
} from 'lucide-react';
import { User as UserIcon } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import type { User } from '../../types';
import { useTheme } from '../../contexts/ThemeContext';
import { supabase } from '../supabaseClient'; // adjust path if needed
import { useAnimation } from '../../contexts/AnimationContext';

export const SettingsView: React.FC = () => {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('profile');
  const [username, setUsername] = useState(user?.username || '');
  const [email, setEmail] = useState(user?.email || '');
  const [bio, setBio] = useState(user?.bio || '');
  const [isEditingBio, setIsEditingBio] = useState(false);
  const [_, setForceUpdate] = useState(0); // for local update
  const [successMessage, setSuccessMessage] = useState('');
  const { enabled: animationsEnabled, toggle: toggleAnimations } = useAnimation();

  const updateUserInSupabase = async (userId: string, username: string, email: string, bio: string) => {
    const { error } = await supabase
      .from('users')
      .update({ username, email, bio })
      .eq('id', userId);
    return error;
  };

  useEffect(() => {
    if (user) {
      setUsername(user.username || '');
      setEmail(user.email || '');
      setBio(user.bio || '');
      // Optionally, fetch from Supabase and update localStorage
      const fetchProfileFromSupabase = async () => {
        const { data, error } = await supabase
          .from('users')
          .select('username, email, bio')
          .eq('id', user.id)
          .single();
        if (!error && data) {
          setUsername(data.username || '');
          setEmail(data.email || '');
          setBio(data.bio || '');
          // Update localStorage with latest from Supabase
          const updatedUser = { ...user, ...data };
          localStorage.setItem('currentUser', JSON.stringify(updatedUser));
        }
      };
      fetchProfileFromSupabase();
    } else {
      const storedUser = localStorage.getItem('currentUser');
      if (storedUser) {
        try {
          const parsed = JSON.parse(storedUser);
          setUsername(parsed.username || '');
          setEmail(parsed.email || '');
          setBio(parsed.bio || '');
        } catch {}
      }
    }
  }, [user]);

  const tabs = [
    { id: 'profile', label: 'Profile', icon: UserIcon },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'data', label: 'Data Management', icon: Database },
    { id: 'appearance', label: 'Appearance', icon: Palette },
  ];

  const handleSaveChanges = async () => {
    if (!user) return;
    const updatedUser: User = { ...user, username, email, bio };
    // Save to localStorage
    localStorage.setItem('currentUser', JSON.stringify(updatedUser));
    // Save to Supabase
    const error = await updateUserInSupabase(user.id, username, email, bio);
    if (!error) {
      setSuccessMessage('Profile saved successfully!');
    } else {
      setSuccessMessage('Saved locally, but failed to sync with Supabase.');
    }
    setTimeout(() => setSuccessMessage(''), 2000);
  };

  const handleEditBio = () => {
    setIsEditingBio(true);
  };

  const handleSaveBio = () => {
    setIsEditingBio(false);
    console.log('Bio:', bio);
  };

  return (
    <div className="space-y-6">
      {successMessage && (
        <div className="fixed top-6 right-6 z-50 px-4 py-2 bg-green-600 text-white rounded shadow-lg animate-fade-in">
          {successMessage}
        </div>
      )}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-3xl font-bold dark:text-white text-black mb-2">Settings</h1>
          <p className="dark:text-gray-400 text-gray-600">Manage your account and application preferences</p>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Settings Navigation */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="rounded-xl p-6 border h-fit dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          <nav className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                    activeTab === tab.id
                      ? 'bg-blue-600 text-white'
                      : 'dark:text-gray-300 text-gray-700 dark:hover:bg-gray-700 hover:bg-gray-100 dark:hover:text-white hover:text-black'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </motion.div>

        {/* Settings Content */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-3 rounded-xl p-6 border dark:bg-gray-800 dark:border-gray-700 bg-white border-gray-200"
        >
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold dark:text-white text-black">Profile Settings</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                    className="w-full rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="w-full rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black"
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center mb-2">
                  <label className="block text-sm font-medium dark:text-gray-300 text-gray-700 mr-2">
                    Bio
                  </label>
                  {!isEditingBio && (
                    <button
                      className="text-blue-400 text-xs underline hover:text-blue-600"
                      onClick={handleEditBio}
                      type="button"
                    >
                      Edit
                    </button>
                  )}
                </div>
                <textarea
                  rows={4}
                  className="w-full rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black"
                  placeholder="Tell us about yourself..."
                  value={bio}
                  onChange={e => setBio(e.target.value)}
                  readOnly={!isEditingBio}
                />
                {isEditingBio && (
                  <div className="flex justify-end mt-2">
                    <button
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm"
                      onClick={handleSaveBio}
                      type="button"
                    >
                      Save
                    </button>
                  </div>
                )}
              </div>

              <div className="flex justify-end">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200"
                  onClick={handleSaveChanges}
                  type="button"
                >
                  <Save className="w-4 h-4" />
                  <span>Save Changes</span>
                </motion.button>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold dark:text-white text-black">Notification Preferences</h2>
              
              <div className="space-y-4">
                {[
                  { label: 'Job Completion', description: 'Get notified when scraping jobs complete' },
                  { label: 'System Alerts', description: 'Receive alerts about system issues' },
                  { label: 'Weekly Reports', description: 'Get weekly performance summaries' },
                  { label: 'Security Notifications', description: 'Important security updates' }
                ].map((notification) => (
                  <div key={notification.label} className="flex items-center justify-between p-4 rounded-lg dark:bg-gray-700/50 bg-gray-100">
                    <div>
                      <h3 className="dark:text-white text-black font-medium">{notification.label}</h3>
                      <p className="dark:text-gray-400 text-gray-600 text-sm">{notification.description}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold dark:text-white text-black">Security Settings</h2>
              
              <div className="space-y-4">
                <div className="p-4 rounded-lg dark:bg-gray-700/50 bg-gray-100">
                  <h3 className="dark:text-white text-black font-medium mb-2">Change Password</h3>
                  <div className="space-y-3">
                    <input
                      type="password"
                      placeholder="Current password"
                      className="w-full rounded-lg px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black"
                    />
                    <input
                      type="password"
                      placeholder="New password"
                      className="w-full rounded-lg px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black"
                    />
                    <input
                      type="password"
                      placeholder="Confirm new password"
                      className="w-full rounded-lg px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black"
                    />
                  </div>
                  <button className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm">
                    Update Password
                  </button>
                </div>

                <div className="p-4 rounded-lg bg-red-900/20 border dark:border-red-800 border-red-300">
                  <h3 className="text-red-400 font-medium mb-2">Danger Zone</h3>
                  <p className="dark:text-gray-400 text-gray-600 text-sm">Permanently delete your account and all associated data</p>
                  <button className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm">
                    <Trash2 className="w-4 h-4" />
                    <span>Delete Account</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'data' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold dark:text-white text-black">Data Management</h2>
              
              <div className="space-y-4">
                <div className="p-4 rounded-lg dark:bg-gray-700/50 bg-gray-100">
                  <h3 className="dark:text-white text-black font-medium mb-2">Export Data</h3>
                  <p className="dark:text-gray-400 text-gray-600 text-sm mb-3">Download all your scraping data and job history</p>
                  <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm">
                    <Download className="w-4 h-4" />
                    <span>Export All Data</span>
                  </button>
                </div>

                <div className="p-4 rounded-lg bg-red-900/20 border dark:border-red-800 border-red-300">
                  <h3 className="text-red-400 font-medium mb-2">Danger Zone</h3>
                  <p className="dark:text-gray-400 text-gray-600 text-sm mb-3">Permanently delete your account and all associated data</p>
                  <button className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm">
                    <Trash2 className="w-4 h-4" />
                    <span>Delete Account</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'appearance' && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold dark:text-white text-black">Appearance Settings</h2>
              
              <div className="space-y-4">
                <div className="p-4 rounded-lg dark:bg-gray-700/50 bg-gray-100">
                  <h3 className="dark:text-white text-black font-medium mb-2">Theme</h3>
                  <p className="dark:text-gray-400 text-gray-600 text-sm mb-3">Choose your preferred theme</p>
                  <div className="flex space-x-3">
                    <button
                      className={`px-4 py-2 rounded-lg text-sm ${theme === 'dark' ? 'bg-blue-600 text-white' : 'bg-gray-600 text-gray-300'}`}
                      onClick={() => theme !== 'dark' && toggleTheme()}
                    >
                      Dark {theme === 'dark' && '(Current)'}
                    </button>
                    <button
                      className={`px-4 py-2 rounded-lg text-sm ${theme === 'light' ? 'bg-blue-600 text-white' : 'bg-gray-600 text-gray-300'}`}
                      onClick={() => theme !== 'light' && toggleTheme()}
                    >
                      Light {theme === 'light' && '(Current)'}
                    </button>
                  </div>
                </div>

                <div className="p-4 rounded-lg dark:bg-gray-700/50 bg-gray-100">
                  <h3 className="dark:text-white text-black font-medium mb-2">Animations</h3>
                  <p className="dark:text-gray-400 text-gray-600 text-sm mb-3">Control interface animations</p>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={animationsEnabled}
                      onChange={toggleAnimations}
                    />
                    <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    <span className="ml-3 text-sm dark:text-gray-300 text-gray-700">Enable animations</span>
                  </label>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};