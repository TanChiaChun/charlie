import { createRouter, createWebHashHistory } from 'vue-router'

import LeaderboardView from '@/views/LeaderboardView.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import UserView from '@/views/UserView.vue'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { component: LeaderboardView, path: '/leaderboard' },
    { component: UserView, path: '/users/:id' },
    { component: NotFoundView, path: '/:pathMatch(.*)*' },
  ],
})

export default router
