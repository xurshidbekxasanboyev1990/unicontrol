/**
 * ============================================
 * UNI CONTROL - Entry Point (main.js)
 * ============================================
 * 
 * Bu fayl Vue ilovasining kirish nuqtasi.
 * 
 * MUHIM: Plugin'larni ulash tartibi muhim!
 * 1. Pinia (state management) - avval ulanishi kerak
 * 2. Router - keyinroq, chunki navigation guards Pinia'dan foydalanadi
 * 
 * Ilova tuzilishi:
 * - App.vue: Root komponent (router-view va ToastContainer)
 * - Pinia stores: auth.js, data.js, toast.js
 * - Router: Barcha sahifalar va navigation guards
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

// Vue ilova instance yaratish
const app = createApp(App)

// Pinia store yaratish (state management)
const pinia = createPinia()

// MUHIM: Avval Pinia ulanadi, chunki Router'ning navigation guards
// Pinia store'lardan (auth.js) foydalanadi
app.use(pinia)

// Router ulash (sahifalar va navigatsiya)
app.use(router)

// Ilovani DOM'ga ulash (#app - index.html'da)
app.mount('#app')
