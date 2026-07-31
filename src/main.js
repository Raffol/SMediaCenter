import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import { installAuthInterceptor } from './api/client'
import { useAuthStore } from './stores/auth'
import './assets/tokens.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// Перехватчик подключается здесь, а не в client.js: иначе router и store
// импортировали бы друг друга по кругу.
installAuthInterceptor(router, useAuthStore(pinia))

app.use(router)
app.mount('#app')
