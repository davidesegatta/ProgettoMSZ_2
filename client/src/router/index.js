import { createRouter, createWebHistory } from 'vue-router'
import process_url from '../components/process_url.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/process_url',
      name: 'process_url',
      component: process_url,
    },
  ]
})

export default router