/**
 * ============================================
 * UNI CONTROL - Til (Language) Store
 * ============================================
 * 
 * Bu store til boshqaruvini amalga oshiradi.
 * localStorage orqali tanlov saqlanadi.
 * 
 * Qo'llanilishi:
 * const { t, locale, setLocale } = useLanguageStore()
 * t('common.save')     → 'Saqlash' / 'Save' / 'Сохранить'
 * t('login.title')     → 'Uni Control'
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import en from '../i18n/en'
import ru from '../i18n/ru'
import uz from '../i18n/uz'

const translations = { uz, ru, en }

export const useLanguageStore = defineStore('language', () => {
    // localStorage dan o'qish yoki default uz
    const locale = ref(localStorage.getItem('unicontrol_locale') || 'uz')

    // Joriy tarjimalar
    const messages = computed(() => translations[locale.value] || translations.uz)

    /**
     * Tilni o'zgartirish
     * @param {string} lang - 'uz' | 'ru' | 'en'
     */
    function setLocale(lang) {
        if (translations[lang]) {
            locale.value = lang
            localStorage.setItem('unicontrol_locale', lang)
        }
    }

    /**
     * Tarjima funksiyasi
     * t('common.save') → 'Saqlash'
     * t('login.title') → 'Uni Control'
     * 
     * @param {string} key - nuqta bilan ajratilgan kalit: 'section.key'
     * @param {object} params - o'rniga qo'yiladigan parametrlar (ixtiyoriy)
     * @returns {string} tarjima yoki kalit o'zi (topilmasa)
     */
    function t(key, params = {}) {
        const keys = key.split('.')
        let result = messages.value

        for (const k of keys) {
            if (result && typeof result === 'object' && k in result) {
                result = result[k]
            } else {
                // Topilmasa, uz dan olishga urinish
                let fallback = translations.uz
                for (const fk of keys) {
                    if (fallback && typeof fallback === 'object' && fk in fallback) {
                        fallback = fallback[fk]
                    } else {
                        return key // Hech qayerda topilmasa kalit qaytadi
                    }
                }
                return typeof fallback === 'string' ? fallback : key
            }
        }

        if (typeof result !== 'string') return key

        // Parametrlarni almashtirish: t('msg', { count: 5 }) → '{count}' → '5'
        if (params && Object.keys(params).length > 0) {
            return result.replace(/\{(\w+)\}/g, (_, paramKey) => {
                return params[paramKey] !== undefined ? params[paramKey] : `{${paramKey}}`
            })
        }

        return result
    }

    /**
     * Mavjud tillar ro'yxati
     */
    const availableLocales = [
        { code: 'uz', name: "O'zbekcha", flag: '🇺🇿' },
        { code: 'ru', name: 'Русский', flag: '🇷🇺' },
        { code: 'en', name: 'English', flag: '🇬🇧' },
    ]

    /**
     * Joriy til nomi
     */
    const currentLocaleName = computed(() => {
        const found = availableLocales.find(l => l.code === locale.value)
        return found ? found.name : "O'zbekcha"
    })

    return {
        locale,
        messages,
        setLocale,
        t,
        availableLocales,
        currentLocaleName,
    }
})
