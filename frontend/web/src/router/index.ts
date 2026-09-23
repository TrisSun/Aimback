import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/api/http'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
        { path: 'detail/:id', name: 'detail', component: () => import('@/views/DetailView.vue') },
        {
          path: 'publish',
          name: 'publish',
          meta: { requiresAuth: true },
          component: () => import('@/views/PublishView.vue'),
        },
        {
          path: 'search',
          name: 'search',
          meta: { requiresAuth: true },
          component: () => import('@/views/SearchView.vue'),
        },
        {
          path: 'mine',
          name: 'mine',
          meta: { requiresAuth: true },
          component: () => import('@/views/MineView.vue'),
        },
      ],
    },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !getToken()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
