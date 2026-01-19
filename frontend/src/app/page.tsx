'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { chatWithStream, healthCheck } from '@/lib/api';
import { t, Language } from '@/lib/translations';
import { useLanguage } from '@/hooks/useLanguage';

/**
 * Message interface represents a single message in the conversation
 * Each message tracks its unique ID, content, sender (user/assistant),
 * topic, and sources for RAG (Retrieval Augmented Generation) responses
 */
interface Message {
  id: string;
  content: string;
  isUser: boolean;
  topic: string;
  sources?: Array<{ title: string; source: string }>;
}

/**
 * Conversation interface represents a chat session
 * Users can maintain multiple conversations, each with its own message history,
 * topic category, and metadata like favorites and session IDs
 */
interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  topic: string;
  timestamp: number;
  sessionId: string;
  isFavorite: boolean;
}

/**
 * Home page component - Main chatbot interface
 * 
 * REFACTORING NOTES (Code Cleanup):
 * - Replaced duplicated language state management with useLanguage() hook
 *   OLD: useState + useEffect for language initialization + event listeners (50+ lines)
 *   NEW: Single useLanguage() call (1 line)
 * 
 * - Removed 2 useEffect hooks that handled:
 *   1) Language loading from localStorage
 *   2) Storage event listeners for multi-tab sync
 *   3) RTL/LTR direction updates
 *   All now handled automatically by useLanguage hook
 * 
 * - Kept essential useEffect hooks for:
 *   1) Auto-scroll to bottom when messages update
 *   2) Backend health check on component mount
 * 
 * BEHAVIOR: No changes to functionality - all language switching,
 * RTL support, and messaging works exactly as before
 */
export default function Home() {
  // ==================== Utility Functions ====================
  
  /**
   * Generate a unique session ID for tracking conversation context
   * Uses cryptographic random bytes encoded as hexadecimal
   */
  const generateSessionId = () => 
    (crypto.getRandomValues(new Uint8Array(16)).reduce(
      (s, b) => s + b.toString(16).padStart(2, '0'), ''
    ));

  // Track message IDs to ensure each message in a session is unique
  const messageIdCounter = useRef(0);
  
  /**
   * Generate unique message ID combining timestamp and counter
   * This ensures uniqueness even if messages are created at same millisecond
   */
  const generateUniqueMessageId = () => {
    const timestamp = Date.now();
    const counter = messageIdCounter.current++;
    return `${timestamp}-${counter}`;
  };

  // ==================== State Management ====================

  /**
   * Conversations state: stores all chat sessions
   * Initialized with one default conversation for user to start typing
   */
  const [conversations, setConversations] = useState<Conversation[]>([
    {
      id: '1',
      title: 'My Trip Plan',
      messages: [],
      topic: 'General',
      timestamp: Date.now(),
      sessionId: generateSessionId(),
      isFavorite: false,
    },
  ]);

  const [currentConversationId, setCurrentConversationId] = useState('1');
  const [inputValue, setInputValue] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  
  /**
   * REFACTORED: Language now managed by custom hook
   * - Replaces: useState('en') + useEffect setup (60+ lines of code)
   * - Single call handles loading, syncing, and RTL updates
   * - Language changes automatically trigger re-render
   */
  const language = useLanguage();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Determine if RTL layout needed (for Arabic language)
  const isRTL = language === 'ar';

  // ==================== Effects ====================

  /**
   * Auto-scroll effect: Keep view at bottom of messages
   * Provides better UX when messages overflow viewport
   */
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversations, currentConversationId]);

  /**
   * Health check effect: Verify backend is available
   * Runs once on component mount
   */
  useEffect(() => {
    const checkBackend = async () => {
      const status = await healthCheck();
      setBackendStatus(status.status);
    };
    checkBackend();
  }, []);

  const getCurrentConversation = () => {
    return conversations.find((c) => c.id === currentConversationId) || conversations[0];
  };

  const getCurrentMessages = () => {
    return getCurrentConversation().messages;
  };

  const handleRecommendedClick = async (recommendation: string) => {
    if (backendStatus !== 'healthy') {
      alert('Backend service is not available. Please try again later.');
      return;
    }

    setIsLoading(true);
    const currentConv = getCurrentConversation();
    const userMessageId = generateUniqueMessageId();
    const assistantMessageId = generateUniqueMessageId();

    const updatedConversations = conversations.map((conv) => {
      if (conv.id === currentConversationId) {
        return {
          ...conv,
          messages: [
            ...conv.messages,
            {
              id: userMessageId,
              content: recommendation,
              isUser: true,
              topic: conv.topic,
            },
            {
              id: assistantMessageId,
              content: '',
              isUser: false,
              topic: conv.topic,
              sources: [],
            },
          ],
        };
      }
      return conv;
    });

    setConversations(updatedConversations);

    try {
      const stream = await chatWithStream({
        message: recommendation,
        session_id: currentConv.sessionId,
        language: language === 'ar' ? 'ar' : 'en',
      });

      const reader = stream.getReader();
      const decoder = new TextDecoder();
      let content = '';
      let sources: Array<{ title: string; source: string }> = [];
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        
        // Keep the last incomplete event in the buffer
        buffer = events.pop() || '';

        for (const event of events) {
          const lines = event.trim().split('\n');
          
          if (lines[0] === 'event: meta' && lines[1]?.startsWith('data:')) {
            try {
              const data = JSON.parse(lines[1].slice(5)) as { sources?: Array<{ title: string; source: string }> };
              sources = data.sources || [];
            } catch (e) {
              // Ignore JSON parse errors
            }
          } else if (lines[0] === 'event: token' && lines[1]?.startsWith('data:')) {
            try {
              // Parse the JSON-encoded token (should be a string)
              const tokenData = JSON.parse(lines[1].slice(5));
              if (typeof tokenData === 'string') {
                content += tokenData;
              } else {
                console.warn('Token is not a string:', tokenData);
              }
            } catch (e) {
              console.warn('Failed to parse token:', lines[1].slice(5), 'Error:', e);
              // Fallback: don't add anything if we can't parse
            }
            setConversations((prevConvs) =>
              prevConvs.map((conv) => {
                if (conv.id === currentConversationId) {
                  const lastMsg = conv.messages[conv.messages.length - 1];
                  if (!lastMsg.isUser) {
                    lastMsg.content = content;
                    lastMsg.sources = sources;
                  }
                }
                return conv;
              })
            );
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setConversations((prevConvs) =>
        prevConvs.map((conv) => {
          if (conv.id === currentConversationId) {
            const lastMsg = conv.messages[conv.messages.length - 1];
            if (!lastMsg.isUser) {
              lastMsg.content = 'Sorry, I encountered an error processing your request.';
            }
          }
          return conv;
        })
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    if (backendStatus !== 'healthy') {
      alert('Backend service is not available. Please try again later.');
      return;
    }

    const messageText = inputValue;
    setInputValue('');
    setIsLoading(true);

    const currentConv = getCurrentConversation();
    const userMessageId = generateUniqueMessageId();
    const assistantMessageId = generateUniqueMessageId();

    const updatedConversations = conversations.map((conv) => {
      if (conv.id === currentConversationId) {
        return {
          ...conv,
          messages: [
            ...conv.messages,
            {
              id: userMessageId,
              content: messageText,
              isUser: true,
              topic: currentConv.topic,
            },
            {
              id: assistantMessageId,
              content: '',
              isUser: false,
              topic: currentConv.topic,
              sources: [],
            },
          ],
        };
      }
      return conv;
    });

    setConversations(updatedConversations);

    try {
      const stream = await chatWithStream({
        message: messageText,
        session_id: currentConv.sessionId,
        language: language === 'ar' ? 'ar' : 'en',
      });

      const reader = stream.getReader();
      const decoder = new TextDecoder();
      let content = '';
      let sources: Array<{ title: string; source: string }> = [];
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        
        // Keep the last incomplete event in the buffer
        buffer = events.pop() || '';

        for (const event of events) {
          const lines = event.trim().split('\n');
          
          if (lines[0] === 'event: meta' && lines[1]?.startsWith('data:')) {
            try {
              const data = JSON.parse(lines[1].slice(5)) as { sources?: Array<{ title: string; source: string }> };
              sources = data.sources || [];
            } catch (e) {
              // Ignore JSON parse errors
            }
          } else if (lines[0] === 'event: token' && lines[1]?.startsWith('data:')) {
            try {
              // Parse the JSON-encoded token (should be a string)
              const tokenData = JSON.parse(lines[1].slice(5));
              if (typeof tokenData === 'string') {
                content += tokenData;
              } else {
                console.warn('Token is not a string:', tokenData);
              }
            } catch (e) {
              console.warn('Failed to parse token:', lines[1].slice(5), 'Error:', e);
              // Fallback: don't add anything if we can't parse
            }
            setConversations((prevConvs) =>
              prevConvs.map((conv) => {
                if (conv.id === currentConversationId) {
                  const lastMsg = conv.messages[conv.messages.length - 1];
                  if (!lastMsg.isUser) {
                    lastMsg.content = content;
                    lastMsg.sources = sources;
                  }
                }
                return conv;
              })
            );
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      setConversations((prevConvs) =>
        prevConvs.map((conv) => {
          if (conv.id === currentConversationId) {
            const lastMsg = conv.messages[conv.messages.length - 1];
            if (!lastMsg.isUser) {
              lastMsg.content = 'Sorry, I encountered an error processing your request.';
            }
          }
          return conv;
        })
      );
    } finally {
      setIsLoading(false);
    }
  };

  const createNewConversation = () => {
    const newId = Date.now().toString();
    const newConversation: Conversation = {
      id: newId,
      title: `Trip ${conversations.length + 1}`,
      messages: [],
      topic: 'General',
      timestamp: Date.now(),
      sessionId: generateSessionId(),
      isFavorite: false,
    };
    setConversations([...conversations, newConversation]);
    setCurrentConversationId(newId);
  };

  const deleteConversation = (id: string) => {
    try {
      const conversationToDelete = conversations.find((c) => c.id === id);
      
      // If chat is empty, keep it open but clear messages
      if (conversationToDelete && conversationToDelete.messages.length === 0) {
        return; // Do nothing - keep empty chat open
      }
      
      // If chat has messages, delete it and create a new one
      if (conversationToDelete && conversationToDelete.messages.length > 0) {
        const filtered = conversations.filter((c) => c.id !== id);
        setConversations(filtered);
        
        if (currentConversationId === id) {
          // Create a new chat instead of switching
          const newId = Date.now().toString();
          const newConversation: Conversation = {
            id: newId,
            title: `Trip ${filtered.length + 1}`,
            messages: [],
            topic: 'General',
            timestamp: Date.now(),
            sessionId: generateSessionId(),
            isFavorite: false,
          };
          setConversations([...filtered, newConversation]);
          setCurrentConversationId(newId);
        }
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
      // Silently fail - don't break the UI
    }
  };

  const toggleFavorite = (id: string) => {
    setConversations((prevConvs) =>
      prevConvs.map((conv) =>
        conv.id === id ? { ...conv, isFavorite: !conv.isFavorite } : conv
      )
    );
  };

  const currentConv = getCurrentConversation();
  const messages = getCurrentMessages();
  const favoriteConversations = conversations.filter((c) => c.isFavorite);
  const recentConversations = conversations.slice(-6);

  return (
    <div className="flex h-screen bg-[#0F1419] text-white">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-0'
        } bg-[#0D0F14] border-r border-[#1A1D25] flex flex-col transition-all duration-300 overflow-hidden`}
      >
        <div className="p-6 border-b border-[#1A1D25]">
          <div className="mb-4">
            <h1 className="text-2xl font-bold text-[#E8A300]">{t('routey', language)}</h1>
            <p className="text-xs text-gray-400 mt-1">{t('tourism_assistant', language)}</p>
          </div>
          <button
            onClick={createNewConversation}
            className="w-full px-4 py-2 bg-[#E8A300] text-black font-semibold rounded-lg hover:bg-[#D4921D] transition"
          >
            {t('new_chat', language)}
          </button>
        </div>

        {/* Favorites Section */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="mb-6">
            <h3 className="text-xs font-semibold text-gray-400 uppercase mb-3 px-2">{t('favorites', language)}</h3>
            {favoriteConversations.length === 0 ? (
              <p className="text-xs text-gray-500 px-2 py-2">{t('no_favorites', language)}</p>
            ) : (
              <div className="space-y-2">
                {favoriteConversations.map((conv) => (
                  <div
                    key={conv.id}
                    className="flex items-center gap-2 px-2 py-1 group"
                  >
                    <button
                      onClick={() => setCurrentConversationId(conv.id)}
                      className={`flex-1 text-left px-2 py-2 rounded text-sm truncate ${
                        currentConversationId === conv.id
                          ? 'bg-[#1A1D25] text-[#E8A300]'
                          : 'text-gray-300 hover:bg-[#1A1D25]'
                      }`}
                    >
                      ⭐ {conv.title}
                    </button>
                    <button
                      onClick={() => toggleFavorite(conv.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-[#E8A300] hover:text-red-400 transition"
                      title="Remove from favorites"
                    >
                      ★
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Conversations */}
          <div>
            <h3 className="text-xs font-semibold text-gray-400 uppercase mb-3 px-2">{t('recent', language)}</h3>
            <div className="space-y-2">
              {recentConversations.map((conv) => (
                <div
                  key={conv.id}
                  className="flex items-center gap-2 px-2 py-1 group"
                >
                  <button
                    onClick={() => setCurrentConversationId(conv.id)}
                    className={`flex-1 text-left px-2 py-2 rounded text-sm truncate ${
                      currentConversationId === conv.id
                        ? 'bg-[#1A1D25] text-[#E8A300]'
                        : 'text-gray-300 hover:bg-[#1A1D25]'
                    }`}
                  >
                    {conv.title}
                  </button>
                  <button
                    onClick={() => toggleFavorite(conv.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-[#E8A300] transition"
                    title={conv.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    {conv.isFavorite ? '★' : '☆'}
                  </button>
                  <button
                    onClick={() => deleteConversation(conv.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-400 transition"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Navigation */}
        <div className="border-t border-[#1A1D25] p-4 flex justify-center gap-6">
          <Link
            href="/settings"
            className="p-3 text-gray-400 hover:text-[#E8A300] hover:bg-[#1A1D25] rounded-lg transition"
            title={t('settings', language)}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.26 2.37 1.805a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.26 3.31-1.805 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.26-2.37-1.805a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.26-3.31 1.805-2.37a1.724 1.724 0 002.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </Link>
          <Link
            href="/help"
            className="p-3 text-gray-400 hover:text-[#E8A300] hover:bg-[#1A1D25] rounded-lg transition"
            title={t('help', language)}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-[#0D0F14] border-b border-[#1A1D25] px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-400 hover:text-white transition p-2"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <p className="text-xs text-gray-500">{t('routey', language)}</p>
              <h1 className="text-xl font-bold text-white">{currentConv.title}</h1>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="mb-8">
                <div className="text-6xl mb-4">🗺️</div>
                <h2 className="text-3xl font-bold mb-2">{t('plan_next_trip', language)}</h2>
                <p className="text-gray-400 mb-8 max-w-md">
                  {t('trip_planning_subtitle', language)}
                </p>
              </div>

              <div className="space-y-3 max-w-sm w-full">
                {[t('top_destinations', language), t('plan_my_trip', language), t('budget_options', language)].map((rec) => (
                  <button
                    key={rec}
                    onClick={() => handleRecommendedClick(rec)}
                    className="w-full px-6 py-3 border border-[#E8A300] text-[#E8A300] rounded-lg hover:bg-[#E8A300] hover:text-black transition font-medium"
                  >
                    {rec}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.isUser ? (
                    <div className="max-w-xs lg:max-w-md xl:max-w-lg bg-[#E8A300] text-black rounded-2xl px-6 py-3">
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  ) : (
                    <div className="max-w-xs lg:max-w-md xl:max-w-lg">
                      <div className="border-l-4 border-[#E8A300] bg-[#1A1D25] rounded-2xl px-6 py-3">
                        <p className="text-gray-100 whitespace-pre-wrap">{msg.content}</p>
                        <div className="mt-3 flex gap-2">
                          <span className="inline-block px-2 py-1 text-xs bg-[#0D0F14] text-[#E8A300] rounded-full">
                            {msg.topic}
                          </span>
                        </div>
                      </div>
                      {msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 bg-[#1A1D25] border border-[#2A2D35] rounded-lg p-3">
                          <h4 className="text-xs font-semibold text-[#E8A300] mb-2">📌 Sources</h4>
                          <ul className="space-y-1">
                            {msg.sources.map((source, idx) => (
                              <li key={idx} className="text-xs text-gray-400">
                                [{idx + 1}] {source.title || 'Source'} — {source.source || 'Italy Tourism'}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-[#0D0F14] border-t border-[#1A1D25] p-6">
          {backendStatus !== 'healthy' && (
            <div className="mb-4 p-3 bg-red-900/30 border border-red-700/50 rounded-lg text-red-300 text-sm">
              ⚠️ {t('backend_warning', language)}
            </div>
          )}
          <form onSubmit={handleSendMessage} className="flex gap-4">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={t('ask_placeholder', language)}
              disabled={isLoading}
              className="flex-1 bg-[#1A1D25] border border-[#2A2D35] rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-[#E8A300] transition disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3 bg-[#E8A300] text-black font-semibold rounded-lg hover:bg-[#D4921D] transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? '⏳' : (language === 'ar' ? 'إرسال' : 'Send')}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
