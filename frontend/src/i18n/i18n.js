import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import all translation resource files
import enTranslation from './locales/en.json';
import esTranslation from './locales/es.json';
import frTranslation from './locales/fr.json';
import zhTranslation from './locales/zh.json';
import jaTranslation from './locales/ja.json';
import koTranslation from './locales/ko.json';
import ruTranslation from './locales/ru.json';
import itTranslation from './locales/it.json';
import fiTranslation from './locales/fi.json';

export const resources = {
  en: { translation: enTranslation },
  es: { translation: esTranslation },
  fr: { translation: frTranslation },
  zh: { translation: zhTranslation },
  ja: { translation: jaTranslation },
  ko: { translation: koTranslation },
  ru: { translation: ruTranslation },
  it: { translation: itTranslation },
  fi: { translation: fiTranslation },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',

    // --- THIS IS THE CORRECTED LINE ---
    // FROM: debug: import.meta.env.DEV,
    // TO:
    // In Create React App, environment variables are accessed via `process.env`.
    // CRA automatically sets `NODE_ENV` to 'development' when you run `npm start`.
    debug: process.env.NODE_ENV === 'development',

    interpolation: {
      escapeValue: false, // React already safes from xss
    },

    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'auraquant-language',
    },
  });

export default i18n;