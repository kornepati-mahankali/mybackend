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
import emailjs from 'emailjs-com';
import { apiService } from '../../services/api';

// IMPORTANT: Use your EmailJS public key (starts with 'public_') from https://dashboard.emailjs.com/admin/account
const SERVICE_ID = 'service_29eid3m'; // from dashboard
const TEMPLATE_ID = 'template_59zd06f'; // from dashboard
const USER_ID = 'BMJxP9EVZiqRMm9C3'; // <-- exactly as shown in your dashboard

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
  const defaultToggles = {
    toolCompletion: false,
    systemAlerts: false,
    weeklyReports: false,
    securityNotifications: false,
  };

  const [toggles, setToggles] = useState(() => {
    const saved = localStorage.getItem('notificationToggles');
    const loaded = saved ? JSON.parse(saved) : defaultToggles;
    console.log('Loaded notification toggles from localStorage:', loaded);
    return loaded;
  });

  useEffect(() => {
    localStorage.setItem('notificationToggles', JSON.stringify(toggles));
  }, [toggles]);

  type ToggleKey = 'toolCompletion' | 'systemAlerts' | 'weeklyReports' | 'securityNotifications';

  // Function to send email using EmailJS
  const sendNotification = (type: ToggleKey, extraData?: any) => {
    let subject = '';
    let message = '';
    // Always use the logged-in user's email
    let toEmail = email; // 'email' comes from useState/user context

    switch (type) {
      case 'toolCompletion':
        subject = 'Tool Completion';
        message = `You have completed ${extraData?.count || 1} tool(s).`;
        break;
      case 'systemAlerts':
        subject = 'System Alert';
        message = 'There is a new system alert for your account.';
        break;
      case 'weeklyReports':
        subject = 'Weekly Report';
        message = 'Here is your weekly performance summary.';
        break;
      case 'securityNotifications':
        subject = 'Security Notification';
        message = 'Important security update for your account.';
        break;
      default:
        return;
    }

    emailjs.send(
      SERVICE_ID,
      TEMPLATE_ID,
      {
        to_email: toEmail,
        subject,
        message,
      },
      USER_ID
    ).then(
      (response) => {
        console.log('Email sent!', response.status, response.text);
      },
      (err) => {
        console.error('Failed to send email:', err);
      }
    );
  };

  // Example: Call this when a tool completes, passing the count
  const onToolComplete = (completedCount: number) => {
    if (toggles.toolCompletion) {
      sendNotification('toolCompletion', { count: completedCount });
    }
  };

  // Example: Call this when a system alert occurs
  const onSystemAlert = () => {
    if (toggles.systemAlerts) {
      sendNotification('systemAlerts');
    }
  };

  // Example: Call this when a weekly report is generated
  const onWeeklyReport = () => {
    if (toggles.weeklyReports) {
      sendNotification('weeklyReports');
    }
  };

  // Example: Call this when a security notification is needed
  const onSecurityNotification = () => {
    if (toggles.securityNotifications) {
      sendNotification('securityNotifications');
    }
  };

  // Toggle handler
  const handleToggle = (key: ToggleKey) => {
    setToggles((prev: typeof defaultToggles) => {
      const newValue = !prev[key];
      // If toggling ON, send notification to the logged-in user's email
      if (newValue && email) {
        sendNotification(key, { to_email: email });
      }
      return { ...prev, [key]: newValue };
    });
  };

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

  // Add state for password change
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Add state for delete account
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteError, setDeleteError] = useState('');
  const [deleteSuccess, setDeleteSuccess] = useState('');
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isExportingData, setIsExportingData] = useState(false);
  const [isExportingFiles, setIsExportingFiles] = useState(false);

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

  const handleExportData = async () => {
    setIsExportingData(true);
    try {
      const data = await apiService.exportUserData();
      
      // Create a blob and download the file
      const blob = new Blob([JSON.stringify(data, null, 2)], { 
        type: 'application/json' 
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `user_data_${user?.id || 'export'}_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccessMessage('Data exported successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
      
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export data. Please try again.');
    } finally {
      setIsExportingData(false);
    }
  };

  const handleExportFiles = async () => {
    setIsExportingFiles(true);
    try {
      const blob = await apiService.exportOutputFiles();
      
      // Download the zip file
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `output_files_${user?.id || 'export'}_${Date.now()}.zip`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      setSuccessMessage('Output files exported successfully!');
      setTimeout(() => setSuccessMessage(''), 3000);
      
    } catch (error) {
      console.error('File export error:', error);
      alert('Failed to export output files. Please try again.');
    } finally {
      setIsExportingFiles(false);
    }
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
                  <label className="block text-sm font-medium mb-2">
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
                  <label className="block text-sm font-medium mb-2">
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
                  <label className="block text-sm font-medium mr-2">
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
                  { key: 'toolCompletion', label: 'Tool Completion', description: 'Get notified when scraping Tool complete' },
                  { key: 'systemAlerts', label: 'System Alerts', description: 'Receive alerts about system issues' },
                  { key: 'weeklyReports', label: 'Weekly Reports', description: 'Get weekly performance summaries' },
                  { key: 'securityNotifications', label: 'Security Notifications', description: 'Important security updates' }
                ].map((notification) => (
                  <div key={notification.key} className="flex items-center justify-between p-4 rounded-lg dark:bg-gray-700/50 bg-gray-100">
                    <div>
                      <h3 className="dark:text-white text-black font-medium">{notification.label}</h3>
                      <p className="dark:text-gray-400 text-gray-600 text-sm">{notification.description}</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        className="sr-only peer"
                        checked={toggles[notification.key]}
                        onChange={() => handleToggle(notification.key as ToggleKey)}
                      />
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
                      value={currentPassword}
                      onChange={e => setCurrentPassword(e.target.value)}
                      disabled={isChangingPassword}
                    />
                    <input
                      type="password"
                      placeholder="New password"
                      className="w-full rounded-lg px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black"
                      value={newPassword}
                      onChange={e => setNewPassword(e.target.value)}
                      disabled={isChangingPassword}
                    />
                    <input
                      type="password"
                      placeholder="Confirm new password"
                      className="w-full rounded-lg px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black"
                      value={confirmNewPassword}
                      onChange={e => setConfirmNewPassword(e.target.value)}
                      disabled={isChangingPassword}
                    />
                  </div>
                  {passwordError && (
                    <div className="mt-2 text-red-500 text-sm">{passwordError}</div>
                  )}
                  {passwordSuccess && (
                    <div className="mt-2 text-green-500 text-sm">{passwordSuccess}</div>
                  )}
                  <button
                    className="mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm disabled:opacity-60"
                    onClick={async () => {
                      setPasswordError('');
                      setPasswordSuccess('');
                      if (!currentPassword || !newPassword || !confirmNewPassword) {
                        setPasswordError('All fields are required.');
                        return;
                      }
                      if (newPassword !== confirmNewPassword) {
                        setPasswordError('New passwords do not match.');
                        return;
                      }
                      setIsChangingPassword(true);
                      try {
                        const res = await fetch('/api/auth/change-password', {
                          method: 'POST',
                          headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                          },
                          body: JSON.stringify({ currentPassword, newPassword, confirmNewPassword }),
                        });
                        const data = await res.json();
                        if (!res.ok) {
                          setPasswordError(data.error || 'Failed to change password.');
                        } else {
                          setPasswordSuccess('Password updated successfully.');
                          setCurrentPassword('');
                          setNewPassword('');
                          setConfirmNewPassword('');
                        }
                      } catch (err) {
                        setPasswordError('Failed to change password.');
                      } finally {
                        setIsChangingPassword(false);
                      }
                    }}
                    disabled={isChangingPassword}
                  >
                    {isChangingPassword ? 'Updating...' : 'Update Password'}
                  </button>
                </div>

                <div className="p-4 rounded-lg bg-red-900/20 border dark:border-red-800 border-red-300">
                  <h3 className="text-red-400 font-medium mb-2">Danger Zone</h3>
                  <p className="dark:text-gray-400 text-gray-600 text-sm">Permanently delete your account and all associated data</p>
                  <button 
                    className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm"
                    onClick={() => setShowDeleteModal(true)}
                  >
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
                  <div className="space-y-3">
                    <button 
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm disabled:opacity-60"
                      onClick={handleExportData}
                      disabled={isExportingData}
                    >
                      <Download className="w-4 h-4" />
                      <span>{isExportingData ? 'Exporting...' : 'Export All Data'}</span>
                    </button>
                    <button 
                      className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm disabled:opacity-60"
                      onClick={handleExportFiles}
                      disabled={isExportingFiles}
                    >
                      <Download className="w-4 h-4" />
                      <span>{isExportingFiles ? 'Exporting...' : 'Export Output Files'}</span>
                    </button>
                  </div>
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

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-red-600 mb-4">Delete Account</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              This action cannot be undone. All your data will be permanently deleted.
            </p>
            <input
              type="password"
              placeholder="Enter your password to confirm"
              className="w-full rounded-lg px-3 py-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white bg-gray-100 border-gray-300 text-black mb-4"
              value={deletePassword}
              onChange={e => setDeletePassword(e.target.value)}
              disabled={isDeletingAccount}
            />
            {deleteError && (
              <div className="mb-4 text-red-500 text-sm">{deleteError}</div>
            )}
            {deleteSuccess && (
              <div className="mb-4 text-green-500 text-sm">{deleteSuccess}</div>
            )}
            <div className="flex space-x-3">
              <button
                className="flex-1 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg text-sm"
                onClick={() => {
                  setShowDeleteModal(false);
                  setDeletePassword('');
                  setDeleteError('');
                  setDeleteSuccess('');
                }}
                disabled={isDeletingAccount}
              >
                Cancel
              </button>
              <button
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm disabled:opacity-60"
                onClick={async () => {
                  setDeleteError('');
                  setDeleteSuccess('');
                  if (!deletePassword) {
                    setDeleteError('Password is required.');
                    return;
                  }
                  setIsDeletingAccount(true);
                  try {
                    const res = await fetch('/api/auth/delete-account', {
                      method: 'DELETE',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('authToken')}`,
                      },
                      body: JSON.stringify({ password: deletePassword }),
                    });
                    const data = await res.json();
                    if (!res.ok) {
                      setDeleteError(data.error || 'Failed to delete account.');
                    } else {
                      setDeleteSuccess('Account deleted successfully. Redirecting...');
                      // Clear local storage and redirect to login
                      setTimeout(() => {
                        localStorage.clear();
                        window.location.href = '/login';
                      }, 2000);
                    }
                  } catch (err) {
                    setDeleteError('Failed to delete account.');
                  } finally {
                    setIsDeletingAccount(false);
                  }
                }}
                disabled={isDeletingAccount}
              >
                {isDeletingAccount ? 'Deleting...' : 'Delete Account'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};