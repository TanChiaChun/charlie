import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/users/:publicId',
      component: (): Promise<typeof import('@/views/UserStepsView.vue')> =>
        import('@/views/UserStepsView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      component: (): Promise<typeof import('@/views/NotFoundView.vue')> =>
        import('@/views/NotFoundView.vue'),
    },
  ],
})

export default router
