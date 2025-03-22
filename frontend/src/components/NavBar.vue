<template>
  
  <nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
      <router-link class="navbar-brand" to="/">Grocery Store</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <!-- Left side links -->
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item" v-if="isLoggedIn && role === 'admin'">
            <router-link class="nav-link" to="/admin-dashboard">Admin Dashboard</router-link>
          </li>
          <li v-if="isLoggedIn && (role === 'admin' || role === 'manager')" class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              Management
            </a>
            <ul class="dropdown-menu">
              <li v-if="role === 'admin' || role === 'manager'">
                <router-link class="dropdown-item" to="/create-category">
                  Create Category
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item" to="/all-categories">
                  View Categories
                </router-link>
              </li>
            </ul>
          </li>
        </ul>
  
        <!-- Right side links -->
        <ul v-if="!isLoggedIn" class="navbar-nav ms-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link" to="/login">Login</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/register">Register</router-link>
          </li>
        </ul>
        
        <ul v-else class="navbar-nav ms-auto mb-2 mb-lg-0">
          <li class="nav-item">
            <router-link class="nav-link position-relative" to="/cart">
              Cart
              <span v-if="cartCount > 0" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger">
                {{ cartCount }}
                <span class="visually-hidden">items in cart</span>
              </span>
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/orders">Orders</router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link" @click="logout">Logout</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
  </template>
  
  <script>
  import userMixin from '../mixins/userMixin'
  
  export default {
      name: "NavBar",
      mixins: [userMixin],
      data() {
          return {
              cartCount: 0
          }
      },
      methods: {
          async fetchCartCount() {
              if (this.isLoggedIn && this.role === 'user') {
                  try {
                      const response = await fetch('http://localhost:5000/view-cart', {
                          headers: {
                              'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                          }
                      });
                      
                      if (response.ok) {
                          const data = await response.json();
                          this.cartCount = data.cart_items?.length || 0;
                      }
                  } catch (error) {
                      console.error('Error fetching cart count:', error);
                  }
              }
          },

      },
      created() {
          this.fetchCartCount();
      },
      watch: {
          isLoggedIn(newVal) {
              if (newVal) this.fetchCartCount();
              else this.cartCount = 0;
          }
      }
  }
  </script>
  
  <style scoped>
  .nav-link {
      cursor: pointer;
  }
  .badge {
      font-size: 0.75em;
      padding: 0.35em 0.65em;
  }
  .dropdown-menu-end {
      right: 0;
      left: auto;
  }
  </style>