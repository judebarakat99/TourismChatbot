"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { updateUserSettings, healthCheck } from "@/lib/api";
import { t, Language } from "@/lib/translations";
import { useLanguage } from "@/hooks/useLanguage";

/**
 * Available language options for the application
 * Provides both English name and native language name for better UX
 */
const languageOptions = [
  { code: "en", name: "English", nativeName: "English" },
  { code: "ar", name: "العربية", nativeName: "Arabic" },
];

/**
 * Settings Page Component
 * 
 * REFACTORING NOTES (Code Cleanup):
 * - Replaced manual language state management with useLanguage() hook
 *   OLD: Load from localStorage + event listeners (40+ lines)
 *   NEW: Single useLanguage() call
 * 
 * - Added separate 'selectedLanguage' state for UI form
 *   This allows user to change selection before saving
 *   Syncs with actual language via useEffect when useLanguage changes
 * 
 * - Removed all event listener setup code (now in custom hook)
 * - Removed RTL direction updates (now automatic via hook)
 * 
 * BEHAVIOR: Language switching works exactly as before
 * - User selects language in dropdown
 * - Clicks "Save Changes"
 * - Language updates across all pages including other tabs
 * - RTL direction applied automatically for Arabic
 */
export default function SettingsPage() {
  /**
   * Current language from custom hook
   * Used for translating UI text on this page
   * Automatically updates when language changes anywhere in app
   */
  const language = useLanguage();
  
  /**
   * Selected language state for the form
   * Allows user to pick language before saving
   * Stays in sync with actual language via useEffect
   */
  const [selectedLanguage, setSelectedLanguage] = useState<Language>('en');
  
  // Other settings state
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [privateProfile, setPrivateProfile] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [backendStatus, setBackendStatus] = useState("checking");

  const isRTL = language === "ar";

  /**
   * Sync selectedLanguage with actual language
   * When language changes (from other tabs or programmatically),
   * update the form to reflect the current selection
   */
  useEffect(() => {
    setSelectedLanguage(language);
  }, [language]);

  /**
   * Health check: Verify backend is available on page load
   */
  useEffect(() => {
    const checkBackend = async () => {
      const status = await healthCheck();
      setBackendStatus(status.status);
    };
    checkBackend();
  }, []);

  const handleSaveSettings = async () => {
    if (backendStatus !== "healthy") {
      setSaveMessage("Backend unavailable");
      return;
    }

    setIsSaving(true);
    setSaveMessage("");
    
    // Save language to localStorage
    localStorage.setItem("language", selectedLanguage);
    
    // Dispatch custom event for same-tab updates
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: { language: selectedLanguage } }));

    try {
      await updateUserSettings({
        notifications_enabled: notificationsEnabled,
        privacy_mode: privateProfile,
        language: selectedLanguage,
      });
      setSaveMessage("Settings saved successfully");
      setTimeout(() => setSaveMessage(""), 3000);
    } catch {
      setSaveMessage("Failed to update profile");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0F1419] text-[#E8E8E8]">
      {/* SIDEBAR */}
      <aside className="w-64 bg-[#0D0F14] flex flex-col border-r border-[#1A1D25] overflow-hidden">
        {/* Top Section */}
        <div className="p-4 border-b border-[#1A1D25]">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-lg">•</span>
            <Link href="/" className="text-lg font-bold text-[#E8A300] hover:opacity-80 transition">
              {t('routey', language)}
            </Link>
            <Link href="/" className="ml-auto text-[#E8A300] text-xl hover:opacity-80 transition">
              +
            </Link>
          </div>

          {/* Search */}
          <div className="relative">
            <input
              type="text"
              placeholder="Contents..."
              className="w-full bg-[#1A1D25] text-[#E8E8E8] placeholder-[#666] text-sm rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-[#E8A300] transition"
            />
            <span className="absolute right-3 top-2.5 text-[#666]">◉</span>
          </div>
        </div>

        {/* Favorites Section */}
        <div className="flex-1 overflow-y-auto">
          <div className="px-4 pt-4">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-xs font-semibold text-[#999] uppercase">Favorites</h3>
              <a href="#" className="text-xs text-[#666] hover:text-[#999] transition">
                View all →
              </a>
            </div>
            <div className="space-y-2">
              <Link
                href="/"
                className="w-full block text-left px-3 py-2 rounded-full text-sm text-[#999] hover:bg-[#1A1D25] transition"
              >
                Home
              </Link>
              <Link
                href="/"
                className="w-full block text-left px-3 py-2 rounded-full text-sm text-[#999] hover:bg-[#1A1D25] transition"
              >
                Chat
              </Link>
            </div>
          </div>

          {/* Recent Section */}
          <div className="px-4 pt-6">
            <div className="flex justify-between items-center mb-2">
              <h3 className="text-xs font-semibold text-[#999] uppercase">Recent</h3>
              <a href="#" className="text-xs text-[#666] hover:text-[#999] transition">
                View all →
              </a>
            </div>
            <div className="text-xs text-[#666] p-3">No recent chats</div>
          </div>
        </div>

        {/* Bottom: User Settings */}
        <div className="border-t border-[#1A1D25] p-4">
          <button className="w-full flex items-center gap-2 text-sm text-[#999] hover:text-[#E8E8E8] transition py-2">
            👤 User Settings
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col bg-[#0F1419]">
        {/* Header with Back Button */}
        <div className="border-b border-[#1A1D25] p-6">
          <div className="max-w-2xl mx-auto flex items-center gap-4">
            <Link
              href="/"
              className="text-[#999] hover:text-[#E8E8E8] transition text-xl"
            >
              ←
            </Link>
            <h1 className="text-3xl font-bold text-[#E8E8E8]">{t('settings', language)}</h1>
          </div>
        </div>

        {/* Settings Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-2xl mx-auto space-y-6">
            {/* Notifications Section */}
            <div className="bg-[#1A1D25] border border-[#2A2D35] rounded-2xl p-6">
              <h2 className="text-xl font-semibold text-[#E8E8E8] mb-4">{t('notifications', language)}</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-sm text-[#E8E8E8]">{t('enable_notifications', language)}</label>
                  <button
                    onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                    className={`w-12 h-6 rounded-full transition ${
                      notificationsEnabled ? "bg-[#E8A300]" : "bg-[#2A2D35]"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full transition transform ${
                        notificationsEnabled ? "translate-x-6" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </div>
                <p className="text-xs text-[#999]">
                  {t('notifications_desc', language)}
                </p>
              </div>
            </div>

            {/* Privacy Section */}
            <div className="bg-[#1A1D25] border border-[#2A2D35] rounded-2xl p-6">
              <h2 className="text-xl font-semibold text-[#E8E8E8] mb-4">{t('privacy', language)}</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <label className="text-sm text-[#E8E8E8]">{t('private_profile', language)}</label>
                  <button
                    onClick={() => setPrivateProfile(!privateProfile)}
                    className={`w-12 h-6 rounded-full transition ${
                      privateProfile ? "bg-[#E8A300]" : "bg-[#2A2D35]"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 bg-white rounded-full transition transform ${
                        privateProfile ? "translate-x-6" : "translate-x-0.5"
                      }`}
                    />
                  </button>
                </div>
                <p className="text-xs text-[#999]">
                  {t('privacy_desc', language)}
                </p>
              </div>
            </div>

            {/* Language Section */}
            <div className="bg-[#1A1D25] border border-[#2A2D35] rounded-2xl p-6">
              <h2 className="text-xl font-semibold text-[#E8E8E8] mb-4">{t('language', language)}</h2>
              <div className="space-y-3">
                <p className="text-xs text-[#999]">{t('language_desc', language)}</p>
                <div className="grid grid-cols-2 gap-2">
                  {languageOptions.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => setSelectedLanguage(lang.code as Language)}
                      className={`px-4 py-3 rounded-lg border transition ${
                        selectedLanguage === lang.code
                          ? "bg-[#E8A300] text-black border-[#E8A300]"
                          : "bg-[#0F1419] text-[#E8E8E8] border-[#2A2D35] hover:border-[#E8A300]"
                      }`}
                    >
                      <div className="font-semibold">{lang.nativeName}</div>
                      <div className="text-xs opacity-75">{lang.name}</div>
                    </button>
                  ))}
                </div>
                {language === "ar" && (
                  <div className="p-3 bg-blue-900/30 border border-blue-700/50 rounded-lg text-blue-300 text-xs">
                    {t('rtl_enabled', language)}
                  </div>
                )}
              </div>
            </div>

            {/* Save Button */}
            <div className="flex gap-3">
              <button
                onClick={handleSaveSettings}
                disabled={isSaving}
                className="flex-1 px-6 py-3 bg-[#E8A300] text-black font-semibold rounded-lg hover:bg-[#D4921D] transition disabled:opacity-50"
              >
                {isSaving ? "⏳ " + t('saving', language) : t('save_changes', language)}
              </button>
              <Link
                href="/"
                className="flex-1 px-6 py-3 bg-[#1A1D25] text-[#E8E8E8] font-semibold rounded-lg hover:bg-[#222530] transition border border-[#2A2D35]"
              >
                {t('back', language)}
              </Link>
            </div>

            {/* Feedback Message */}
            {saveMessage && (
              <div
                className={`p-4 rounded-lg text-center ${
                  saveMessage.includes("✅")
                    ? "bg-green-900/30 text-green-300 border border-green-700/50"
                    : "bg-red-900/30 text-red-300 border border-red-700/50"
                }`}
              >
                {saveMessage}
              </div>
            )}

            {backendStatus !== "healthy" && (
              <div className="p-4 rounded-lg bg-yellow-900/30 text-yellow-300 border border-yellow-700/50">
                {t('backend_warning', language)}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
