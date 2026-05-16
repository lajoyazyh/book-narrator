import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/pages/HomePage.vue'
import BookNarratorPage from '@/pages/BookNarratorPage.vue'
import NarrationHistoryPage from '@/pages/NarrationHistoryPage.vue'
import FavoritesPage from '@/pages/FavoritesPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomePage
    },
    {
      path: '/book-narrator',
      name: 'book-narrator',
      component: BookNarratorPage
    },
    {
      path: '/narration-history',
      name: 'narration-history',
      component: NarrationHistoryPage
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: FavoritesPage
    }
  ]
})

export default router
