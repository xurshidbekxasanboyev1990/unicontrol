import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/styles/main.css'

const app = createApp(App)
const pinia = createPinia()

// Avval Pinia, keyin Router
app.use(pinia)
app.use(router)

app.mount('#app')
