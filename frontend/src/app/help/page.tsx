"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { t, Language } from "@/lib/translations";

export default function HelpPage() {
  // Initialize language from localStorage
  const [language, setLanguage] = useState<Language>(() => {
    if (typeof window !== 'undefined') {
      return (localStorage.getItem("language") as Language) || "en";
    }
    return "en";
  });
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  useEffect(() => {
    // Apply RTL direction based on language
    document.documentElement.dir = language === "ar" ? "rtl" : "ltr";

    // Listen for storage changes (when language changes on settings page)
    const handleStorageChange = () => {
      const newLanguage = localStorage.getItem("language") as Language || "en";
      setLanguage(newLanguage);
      document.documentElement.dir = newLanguage === "ar" ? "rtl" : "ltr";
    };

    // Listen for custom language change event (same tab)
    const handleLanguageChanged = (event: Event) => {
      const customEvent = event as CustomEvent;
      const newLanguage = customEvent.detail.language as Language;
      setLanguage(newLanguage);
      document.documentElement.dir = newLanguage === "ar" ? "rtl" : "ltr";
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('languageChanged', handleLanguageChanged);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('languageChanged', handleLanguageChanged);
    };
  }, []);

  const faqs = [
    {
      question: t('faq_1_q', language),
      answer: t('faq_1_a', language),
    },
    {
      question: t('faq_2_q', language),
      answer: t('faq_2_a', language),
    },
    {
      question: t('faq_3_q', language),
      answer: t('faq_3_a', language),
    },
    {
      question: t('faq_4_q', language),
      answer: t('faq_4_a', language),
    },
    {
      question: t('faq_5_q', language),
      answer: t('faq_5_a', language),
    },
    {
      question: t('faq_6_q', language),
      answer: t('faq_6_a', language),
    },
  ];

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
              className="block w-full text-left px-3 py-2 rounded-lg text-sm bg-[#1A1D25] text-[#E8A300] hover:bg-[#222530] transition"
            >
              🏠 {t('back_to_chat', language)}
            </Link>
            <Link
              href="/settings"
              className="block w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition"
            >
              ⚙️ {t('settings', language)}
            </Link>
            <Link
              href="/account"
              className="block w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition"
            >
              👤 {t('account', language)}
            </Link>
          </div>
        </div>

        {/* Help Categories */}
        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-xs font-semibold text-[#999] uppercase mb-3">{t('support_topics', language)}</h3>
          <div className="space-y-2">
            <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition">
              {t('getting_started', language)}
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition">
              {t('chat_features', language)}
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition">
              {t('account_privacy', language)}
            </button>
            <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-[#999] hover:bg-[#1A1D25] transition">
              {t('travel_tips', language)}
            </button>
          </div>
        </div>

        {/* Contact Support */}
        <div className="border-t border-[#1A1D25] p-4">
          <div className="bg-[#1A1D25] rounded-lg p-3">
            <h4 className="text-sm font-semibold text-[#E8A300] mb-2">{t('need_help', language)}</h4>
            <p className="text-xs text-[#999] mb-3">{t('contact_support', language)}</p>
            <a
              href="mailto:support@routey.com"
              className="block w-full text-center px-3 py-2 bg-[#E8A300] text-black font-semibold rounded-lg hover:bg-[#D4921D] transition text-sm"
            >
              {t('email_support', language)}
            </a>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col bg-[#0F1419]">
        {/* Header */}
        <div className="border-b border-[#1A1D25] p-6">
          <div className="max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold text-[#E8E8E8]">{t('help_title', language)}</h1>
            <p className="text-sm text-[#999] mt-2">{t('help_subtitle', language)}</p>
          </div>
        </div>

        {/* Help Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto space-y-4">
            {/* FAQs */}
            <div className="space-y-3">
              {faqs.map((faq, idx) => (
                <div
                  key={idx}
                  className="bg-[#1A1D25] border border-[#2A2D35] rounded-lg overflow-hidden hover:border-[#E8A300]/50 transition"
                >
                  <button
                    onClick={() => setExpandedIndex(expandedIndex === idx ? null : idx)}
                    className="w-full flex justify-between items-center px-6 py-4 hover:bg-[#222530] transition text-left"
                  >
                    <span className="font-semibold text-[#E8E8E8]">{faq.question}</span>
                    <span className={`text-[#E8A300] transition-transform ${expandedIndex === idx ? "rotate-180" : ""}`}>
                      ▼
                    </span>
                  </button>
                  {expandedIndex === idx && (
                    <div className="px-6 py-4 bg-[#0F1419] border-t border-[#2A2D35] text-[#999] text-sm leading-relaxed">
                      {faq.answer}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Additional Resources */}
            <div className="mt-8 bg-[#1A1D25] border border-[#2A2D35] rounded-lg p-6">
              <h2 className="text-xl font-semibold text-[#E8E8E8] mb-4">📚 Additional Resources</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <a
                  href="#"
                  className="p-4 bg-[#0F1419] border border-[#2A2D35] rounded-lg hover:border-[#E8A300] transition"
                >
                  <h3 className="font-semibold text-[#E8A300] mb-1">📖 Documentation</h3>
                  <p className="text-xs text-[#999]">Read our full documentation and guides</p>
                </a>
                <a
                  href="#"
                  className="p-4 bg-[#0F1419] border border-[#2A2D35] rounded-lg hover:border-[#E8A300] transition"
                >
                  <h3 className="font-semibold text-[#E8A300] mb-1">🐛 Report a Bug</h3>
                  <p className="text-xs text-[#999]">Let us know if you found any issues</p>
                </a>
                <a
                  href="#"
                  className="p-4 bg-[#0F1419] border border-[#2A2D35] rounded-lg hover:border-[#E8A300] transition"
                >
                  <h3 className="font-semibold text-[#E8A300] mb-1">💡 Feature Request</h3>
                  <p className="text-xs text-[#999]">Suggest new features for Routey</p>
                </a>
                <a
                  href="#"
                  className="p-4 bg-[#0F1419] border border-[#2A2D35] rounded-lg hover:border-[#E8A300] transition"
                >
                  <h3 className="font-semibold text-[#E8A300] mb-1">🌐 Community Forum</h3>
                  <p className="text-xs text-[#999]">Join our community of travelers</p>
                </a>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-8 text-center p-6 bg-[#1A1D25] border border-[#2A2D35] rounded-lg">
              <p className="text-sm text-[#999]">
                Can&apos;t find what you&apos;re looking for?{" "}
                <a href="mailto:support@routey.com" className="text-[#E8A300] hover:underline">
                  Contact support
                </a>
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
