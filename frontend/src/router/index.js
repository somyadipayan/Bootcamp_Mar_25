import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegistrationPage from '@/views/RegistrationPage.vue'
import LoginPage from '@/views/LoginPage.vue'
import CreateCategory from '@/views/CreateCategory.vue'
import AllCategories from '@/views/AllCategories.vue'
import UpdateCategory from '@/views/UpdateCategory.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/register',
    name: 'register',
    component: RegistrationPage
  },
  {
    path: '/about',
    name: 'about',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/AboutView.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: LoginPage
  },
  {
    path: '/create-category',
    name: 'createcategory',
    component: CreateCategory
  },
  {
    path: '/all-categories',
    name: 'allcategories',
    component: AllCategories
  },
  {
    path: '/update-category/:id',
    name: 'updatecategory',
    component: UpdateCategory
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
