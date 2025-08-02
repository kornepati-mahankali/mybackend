import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  X, 
  Minimize2, 
  Maximize2,
  Sparkles,
  Wrench,
  Lightbulb,
  HelpCircle,
  Settings,
  Download,
  Play,
  AlertCircle,
  CheckCircle,
  Copy,
  ExternalLink,
  Star,
  Zap,
  Shield,
  Globe,
  TrendingUp
} from 'lucide-react';

const apiKey = import.meta.env.VITE_GROQ_API_KEY;

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  toolSuggestions?: Array<{
    name: string;
    category: string;
    description: string;
  }>;
}

interface AIAssistantProps {
  isOpen: boolean;
  onToggle: () => void;
  isMinimized?: boolean;
  onMinimize?: () => void;
  className?: string;
  variant?: 'homepage' | 'dashboard';
}

export const AIAssistant: React.FC<AIAssistantProps> = ({
  isOpen,
  onToggle,
  isMinimized = false,
  onMinimize,
  className = '',
  variant = 'dashboard'
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: `🎉 Welcome to ScraperPro AI Assistant!\n\nI'm here to help you master web scraping with intelligent guidance and personalized recommendations.\n\n**What I can help you with:**\n• 🛠️ **Tool Selection**: Find the perfect scraping tools for your needs\n• ⚙️ **Configuration**: Step-by-step setup guidance\n• 🔧 **Troubleshooting**: Resolve issues quickly\n• 📈 **Performance**: Optimize your scraping success rates\n• 💡 **Best Practices**: Learn industry-standard techniques\n\n**Quick Start Tips:**\n• Ask me about specific tools (Gem, Global, E-Procurement)\n• Get help with configuration and setup\n• Learn about data export formats\n• Troubleshoot common issues\n\nWhat would you like to explore today?`,
      timestamp: new Date()
    }
  ]);

  // Check API key availability on component mount
  useEffect(() => {
    if (!apiKey) {
      setMessages(prev => [...prev, {
        id: '2',
        type: 'assistant',
        content: '⚠️ **API Key Status**: The GROQ API key is not currently available. Please restart your development server after adding the API key to your `.env` file.',
        timestamp: new Date()
      }]);
    }
  }, [apiKey]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(true);
  const [showTypingIndicator, setShowTypingIndicator] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    // Check if API key is available
    if (!apiKey) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: '❗ **API Key Missing**: The GROQ API key is not configured.\n\n**To fix this:**\n1. Make sure you have `VITE_GROQ_API_KEY` in your `.env` file\n2. Restart your development server\n3. The API key should be in format: `gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`\n\n**Note**: The API key has been added to your `.env` file. Please restart the development server for the changes to take effect.',
        timestamp: new Date()
      }]);
      return;
    }
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setShowTypingIndicator(true);
    try {
      const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${apiKey}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          model: "llama3-70b-8192",
          messages: [{ role: "user", content: userMessage.content }]
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to get response');
      }
      const data = await response.json();
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.choices[0].message.content,
        timestamp: new Date(),
        toolSuggestions: []
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsConnected(true);
      setShowTypingIndicator(false);
    } catch (error) {
      setIsConnected(false);
      let errorContent = `⚠️ **Service Error**: I'm having trouble processing your request.\n\n**Error Details:** ${error instanceof Error ? error.message : 'Unknown error'}\n\nPlease check your API key and try again.`;
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: errorContent,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setShowTypingIndicator(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const quickQuestions = [
    {
      text: "How do I configure a new scraping job?",
      icon: <Settings className="w-3 h-3" />,
      category: "setup"
    },
    {
      text: "Which tool is best for e-commerce data?",
      icon: <Globe className="w-3 h-3" />,
      category: "tools"
    },
    {
      text: "How can I improve my success rate?",
      icon: <TrendingUp className="w-3 h-3" />,
      category: "performance"
    },
    {
      text: "What export formats are available?",
      icon: <Download className="w-3 h-3" />,
      category: "export"
    },
    {
      text: "How do I troubleshoot failed jobs?",
      icon: <AlertCircle className="w-3 h-3" />,
      category: "troubleshooting"
    }
  ];

  const handleQuickQuestion = (question: { text: string; icon: JSX.Element; category: string }) => {
    setInputValue(question.text);
    setTimeout(() => handleSendMessage(), 100);
  };

  if (!isOpen) {
    // For homepage variant, don't show the floating button when closed
    if (variant === 'homepage') {
      return null;
    }
    return (
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={onToggle}
        className={`fixed bottom-6 right-6 w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center z-50 ${className}`}
      >
        <MessageCircle className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
        <div className="absolute -top-1 -right-1 w-3 h-3 sm:w-4 sm:h-4 bg-green-400 rounded-full animate-pulse"></div>
      </motion.button>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 10 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 10 }}
        transition={{ duration: 0.1 }}
        className={`fixed bottom-0 left-0 right-0 mx-auto w-full max-w-full sm:bottom-6 sm:right-6 sm:left-auto sm:translate-x-0 sm:w-96 sm:max-w-md h-[80vh] max-h-[600px] bg-white/95 dark:bg-gray-900/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50 flex flex-col z-50 overflow-x-hidden ${className}`}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-t-2xl relative overflow-hidden">
          {/* Animated background */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 via-purple-600/20 to-indigo-600/20 animate-pulse"></div>
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 via-yellow-400 to-red-400"></div>
          <div className="flex items-center space-x-3 relative z-10">
            <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/30">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-white font-bold text-lg">AI Assistant</h3>
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
                <span className="text-white/90 text-xs font-medium">
                  {isConnected ? 'Online & Ready' : connectionError || 'Offline'}
                </span>
                {isConnected && <Sparkles className="w-3 h-3 text-yellow-300 animate-pulse" />}
                {!isConnected && <AlertCircle className="w-3 h-3 text-red-300" />}
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-2 relative z-10">
            {onMinimize && (
              <button
                onClick={onMinimize}
                className="text-white/80 hover:text-white transition-all duration-200 hover:scale-110 p-1 rounded-lg hover:bg-white/10"
              >
                {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
              </button>
            )}
            <button
              onClick={onToggle}
              className="text-white/80 hover:text-white transition-all duration-200 hover:scale-110 p-1 rounded-lg hover:bg-white/10"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 w-full break-words">
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.1 }}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex items-start space-x-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'user' 
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600' 
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}>
                  {message.type === 'user' ? (
                    <User className="w-4 h-4 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                  )}
                </div>
                <div className={`rounded-2xl px-4 py-3 shadow-lg ${
                  message.type === 'user'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 text-gray-900 dark:text-gray-100 border border-gray-200/50 dark:border-gray-600/50'
                }`}>
                  <div className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</div>
                  {/* Tool Suggestions */}
                  {message.toolSuggestions && message.toolSuggestions.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200/50 dark:border-gray-600/50">
                      <div className="flex items-center space-x-2 mb-3">
                        <Wrench className="w-4 h-4 text-blue-500" />
                        <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                          🎯 Recommended Tool
                        </span>
                      </div>
                      {message.toolSuggestions.map((tool, index) => (
                        <div key={index} className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 rounded-xl p-3 border border-blue-200/50 dark:border-blue-700/50 shadow-sm">
                          <div className="flex items-center justify-between mb-1">
                            <div className="font-semibold text-sm text-blue-800 dark:text-blue-200">{tool.name}</div>
                            <button 
                              onClick={() => navigator.clipboard.writeText(tool.name)}
                              className="text-blue-500 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
                            >
                              <Copy className="w-3 h-3" />
                            </button>
                          </div>
                          <div className="text-xs text-gray-600 dark:text-gray-400">{tool.description}</div>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="text-xs opacity-70 mt-1">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
          {showTypingIndicator && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="flex items-start space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-2xl px-4 py-3 shadow-lg border border-gray-200/50 dark:border-gray-600/50">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">AI is thinking...</span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>
        {/* Quick Questions */}
        {messages.length === 1 && (
          <div className="px-4 pb-2">
            <div className="text-xs text-gray-500 dark:text-gray-400 mb-2 font-medium">
              Quick Questions:
            </div>
            <div className="flex flex-wrap gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickQuestion(question)}
                  className="text-xs bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 hover:from-blue-100 hover:to-purple-100 dark:hover:from-blue-800/30 dark:hover:to-purple-800/30 text-gray-700 dark:text-gray-300 px-3 py-2 rounded-full transition-all duration-200 flex items-center space-x-1 border border-blue-200 dark:border-blue-800"
                >
                  {question.icon}
                  <span>{question.text}</span>
                </button>
              ))}
            </div>
          </div>
        )}
        {/* Input */}
        <div className="p-4 border-t border-gray-200/50 dark:border-gray-700/50 bg-gradient-to-r from-gray-50/50 to-gray-100/50 dark:from-gray-800/50 dark:to-gray-700/50">
          <div className="flex space-x-2">
            <div className="flex-1 relative">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about scraping tools, configuration, or troubleshooting..."
                className="w-full bg-white border border-gray-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition-all duration-200 text-gray-900 dark:bg-gray-800 dark:text-white"
                disabled={isLoading}
              />
              {inputValue && (
                <button
                  onClick={() => setInputValue('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white p-3 rounded-xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
          {/* Quick Tips */}
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
            💡 Press Enter to send • Use quick questions above for common topics
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}; 