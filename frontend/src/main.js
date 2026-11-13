import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Login from './Login.vue'
import Catalog from './Catalog.vue'
import { signedIn } from './api'
import './style.css'

const catalogPath = '/catalog/:section(pets|breeds|species)'
const routes = [
  { path: '/login', name: 'login', component: Login },
  { path: catalogPath, name: 'list', component: Catalog, meta: { private: true } },
  { path: catalogPath + '/new', name: 'new', component: Catalog, meta: { private: true } },
  { path: catalogPath + '/:id(\\d+)', name: 'detail', component: Catalog, meta: { private: true } },
  { path: catalogPath + '/:id(\\d+)/edit', name: 'edit', component: Catalog, meta: { private: true } },
  { path: '/:missing(.*)*', redirect: '/catalog/pets' },
]
const router = createRouter({ history: createWebHistory(), routes })
router.beforeEach(to => {
  if (to.meta.private && !signedIn()) return { name: 'login', query: { next: to.fullPath } }
  if (to.name === 'login' && signedIn()) return '/catalog/pets'
})

createApp(App).use(router).mount('#app')
