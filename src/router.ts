import { createRouter, createWebHistory } from 'vue-router'
import CarsPage from '@/views/CarsPage.vue'
import UsersPage from '@/views/UsersPage.vue'

const routes = [
  { path: '/', redirect: '/cars' },
  { path: '/cars', component: CarsPage },
  { path: '/users', component: UsersPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
