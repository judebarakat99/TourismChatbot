"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { updateUserProfile, deleteUserAccount, getUserProfile, healthCheck } from "@/lib/api";
import { t, Language } from "@/lib/translations";
import { useLanguage } from "@/hooks/useLanguage";

export default function AccountPage() {
  const language = useLanguage();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [message, setMessage] = useState("");
  const [backendStatus, setBackendStatus] = useState("checking");

  const isRTL = language === "ar";

  useEffect(() => {
    const checkBackend = async () => {
      const status = await healthCheck();
      setBackendStatus(status.status);
      if (status.status === "healthy") {
        try {
          const profile = await getUserProfile();
          setName(profile.name || "");
          setEmail(profile.email || "");
        } catch (error) {
          console.error("Failed to load profile:", error);
        }
      }
    };
    checkBackend();
  }, []);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim() || !email.trim()) {
      setMessage("❌ " + t('name_email_required', language));
      return;
    }

    if (password && password !== confirmPassword) {
      setMessage("❌ " + t('passwords_dont_match', language));
      return;
    }

    setIsSaving(true);
    setMessage("");

    try {
      await updateUserProfile({
        name,
        email,
      });
      setMessage("✅ " + t('profile_updated', language));
      setPassword("");
      setConfirmPassword("");
      setTimeout(() => setMessage(""), 3000);
    } catch {
      setMessage("❌ " + t('failed_update', language));
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      await deleteUserAccount();
      setMessage("✅ " + t('account_deleted', language));
      setTimeout(() => (window.location.href = "/"), 2000);
    } catch {
      setMessage("❌ " + t('failed_delete', language));
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
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

          {/* Quick Links */}
          <div className="space-y-2">
            <Link
              href="/"
              className="block w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition"
            >
              🏠 Back to Chat
            </Link>
            <Link
              href="/settings"
              className="block w-full text-left px-3 py-2 rounded-lg text-sm bg-[#1A1D25] text-[#E8A300] hover:bg-[#222530] transition"
            >
              ⚙️ Settings
            </Link>
          </div>
        </div>

        {/* Account Menu */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-xs font-semibold text-[#999] uppercase mb-3">Account</h3>
          <div className="space-y-2">
            <button className="w-full text-left px-3 py-2 rounded-lg text-sm bg-[#1A1D25] text-[#E8A300] hover:bg-[#222530] transition">
              👤 Profile
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition">
              🔐 Security
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition">
              🗑️ Delete Account
            </button>
          </div>
        </div>

        {/* Contact Support */}
        <div className="border-t border-[#1A1D25] p-4">
          <div className="bg-[#1A1D25] rounded-lg p-3">
            <h4 className="text-sm font-semibold text-[#E8A300] mb-2">Need Help?</h4>
            <p className="text-xs text-[#999] mb-3">Contact our support team</p>
            <a
              href="mailto:support@routey.com"
              className="block w-full text-center px-3 py-2 bg-[#E8A300] text-black font-semibold rounded-lg hover:bg-[#D4921D] transition text-sm"
            >
              📧 Email
            </a>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col bg-[#0F1419]">
        {/* Header */}
        <div className="border-b border-[#1A1D25] p-6">
          <div className="max-w-2xl mx-auto flex items-center gap-4">
            <h1 className="text-3xl font-bold text-[#E8E8E8]">👤 {t('account_title', language)}</h1>
          </div>
        </div>

        {/* Account Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-2xl mx-auto space-y-6">
            {/* Profile Section */}
            <form onSubmit={handleSaveProfile} className="bg-[#1A1D25] border border-[#2A2D35] rounded-2xl p-6">
              <h2 className="text-xl font-semibold text-[#E8E8E8] mb-4">{t('profile_information', language)}</h2>
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-[#999]">{t('full_name', language)}</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-[#0F1419] text-[#E8E8E8] border border-[#2A2D35] rounded-lg px-4 py-2 mt-2 outline-none focus:ring-1 focus:ring-[#E8A300] transition"
                    placeholder={t('full_name_placeholder', language)}
                  />
                </div>
                <div>
                  <label className="text-sm text-[#999]">{t('email_address', language)}</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-[#0F1419] text-[#E8E8E8] border border-[#2A2D35] rounded-lg px-4 py-2 mt-2 outline-none focus:ring-1 focus:ring-[#E8A300] transition"
                    placeholder={t('email_placeholder', language)}
                  />
                </div>
                <div>
                  <label className="text-sm text-[#999]">{t('new_password', language)}</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-[#0F1419] text-[#E8E8E8] border border-[#2A2D35] rounded-lg px-4 py-2 mt-2 outline-none focus:ring-1 focus:ring-[#E8A300] transition"
                    placeholder="Leave blank to keep current password"
                  />
                </div>
                <div>
                  <label className="text-sm text-[#999]">Confirm Password</label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full bg-[#0F1419] text-[#E8E8E8] border border-[#2A2D35] rounded-lg px-4 py-2 mt-2 outline-none focus:ring-1 focus:ring-[#E8A300] transition"
                    placeholder={t('confirm_password_placeholder', language)}
                  />
                </div>
                <button
                  type="submit"
                  disabled={isSaving}
                  className="w-full bg-[#E8A300] hover:bg-[#D4921D] text-black font-semibold py-2 px-6 rounded-lg transition disabled:opacity-50"
                >
                  {isSaving ? "⏳ " + t('saving', language) : t('save_changes', language)}
                </button>
              </div>
            </form>

            {/* Security Section */}
            <div className="bg-[#1A1D25] border border-[#2A2D35] rounded-2xl p-6">
              <h2 className="text-xl font-semibold text-[#E8E8E8] mb-4">{t('security', language)}</h2>
              <div className="space-y-2">
                <button className="w-full flex justify-between items-center text-left px-4 py-3 rounded-lg hover:bg-[#222530] transition text-sm">
                  <span>{t('change_password', language)}</span>
                  <span className="text-[#999]">›</span>
                </button>
                <button className="w-full flex justify-between items-center text-left px-4 py-3 rounded-lg hover:bg-[#222530] transition text-sm">
                  <span>{t('two_factor', language)}</span>
                  <span className="text-[#999]">›</span>
                </button>
                <button className="w-full flex justify-between items-center text-left px-4 py-3 rounded-lg hover:bg-[#222530] transition text-sm">
                  <span>{t('active_sessions', language)}</span>
                  <span className="text-[#999]">›</span>
                </button>
              </div>
            </div>

            {/* Danger Zone */}
            <div className="bg-red-900/20 border border-red-800 rounded-2xl p-6">
              <h2 className="text-xl font-semibold text-red-400 mb-4">{t('danger_zone', language)}</h2>
              <p className="text-sm text-red-300 mb-4">{t('delete_account_warning', language)}</p>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-6 rounded-lg transition"
              >
                {t('delete_account', language)}
              </button>
            </div>

            {/* Delete Confirmation Modal */}
            {showDeleteConfirm && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-[#1A1D25] border border-red-800 rounded-2xl p-6 max-w-sm">
                  <h3 className="text-xl font-semibold text-red-400 mb-4">{t('delete_confirm_title', language)}</h3>
                  <p className="text-sm text-gray-300 mb-6">
                    {t('delete_confirm_message', language)}
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => setShowDeleteConfirm(false)}
                      className="flex-1 px-4 py-2 bg-[#2A2D35] text-[#E8E8E8] rounded-lg hover:bg-[#333538] transition"
                    >
                      {t('cancel', language)}
                    </button>
                    <button
                      onClick={handleDeleteAccount}
                      disabled={isDeleting}
                      className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50"
                    >
                      {isDeleting ? "⏳..." : "Delete"}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Feedback Messages */}
            {message && (
              <div
                className={`p-4 rounded-lg text-center ${
                  message.includes("✅")
                    ? "bg-green-900/30 text-green-300 border border-green-700/50"
                    : "bg-red-900/30 text-red-300 border border-red-700/50"
                }`}
              >
                {message}
              </div>
            )}

            {backendStatus !== "healthy" && (
              <div className="p-4 rounded-lg bg-yellow-900/30 text-yellow-300 border border-yellow-700/50">
                ⚠️ Backend unavailable - changes will be saved locally
              </div>
            )}

            {/* Back Button */}
            <Link
              href="/settings"
              className="block text-center px-6 py-3 bg-[#1A1D25] text-[#E8E8E8] font-semibold rounded-lg hover:bg-[#222530] transition border border-[#2A2D35]"
            >
              ← Back to Settings
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
