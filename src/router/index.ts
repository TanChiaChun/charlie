import { createRouter, createWebHashHistory } from 'vue-router'
import NotFoundView from '@/views/NotFoundView.vue'
import UserView from '@/views/UserView.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/users/:id', component: UserView },
    { path: '/:pathMatch(.*)*', component: NotFoundView },
  ],
})

export default router
