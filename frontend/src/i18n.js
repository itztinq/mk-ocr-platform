import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enCommon from './locales/en/common.json';
import mkCommon from './locales/mk/common.json';

const savedLanguage = localStorage.getItem('language');

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en: {
        common: enCommon,
      },
      mk: {
        common: mkCommon,
      },
    },
    lng: savedLanguage || 'en',
    fallbackLng: 'en',
    supportedLngs: ['en', 'mk'],
    defaultNS: 'common',
    ns: ['common'],
    interpolation: {
      escapeValue: false,
    },
    returnNull: false,
  });

i18n.on('languageChanged', (lng) => {
  localStorage.setItem('language', lng);
  document.documentElement.setAttribute('lang', lng);
});

document.documentElement.setAttribute('lang', i18n.language);

export default i18n;