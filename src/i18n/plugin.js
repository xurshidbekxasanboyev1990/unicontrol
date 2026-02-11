/**
 * i18n Plugin for Vue
 * 
 * Bu plugin barcha komponentlarga t() funksiyasini 
 * global provide/inject orqali taqdim etadi.
 * 
 * Qo'llanilishi:
 * Template'da: {{ t('common.save') }}
 * Script'da: const { t } = inject('i18n')
 */

import { useLanguageStore } from '../stores/language'

export default {
    install(app) {
        // Provide t function globally
        app.config.globalProperties.$t = function (key, params) {
            const langStore = useLanguageStore()
            return langStore.t(key, params)
        }

        // Also provide via provide/inject pattern
        app.provide('i18n', {
            get t() {
                const langStore = useLanguageStore()
                return langStore.t
            },
            get locale() {
                const langStore = useLanguageStore()
                return langStore.locale
            },
            get setLocale() {
                const langStore = useLanguageStore()
                return langStore.setLocale
            }
        })
    }
}
