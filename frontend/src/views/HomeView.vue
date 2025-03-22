<template>
  <NavBar/>
  <div class="container mt-5">
    <h2>Welcome to our Store</h2>
    <p v-if="user">Hello, {{ user.username }}</p>
    <p v-else>Please login to shop using our application</p>
    <!-- SERACHBAR -->
     <input type="text" v-model="searchQuery" placeholder="Search for products" class="form-control mt-3">
    <div v-for="category in filteredCategories" :key="category.id" class="mt-3">
      <h4>{{ category.name }}</h4>
      <div class="row">
        <div v-for="product in category.products" :key="product.id" class="col-md-3 mb-3">
          <div class="card">
            <div class="card-body">
              <h5 class="card-title">{{ product.name }}</h5>
              <p class="card-text">Rs.{{ product.price }}/{{ product.unit }}</p>
              <input type="number" v-model="quantities[product.id]" class="form-control mb-2" placeholder="Quantity">
              <button v-if="user" class="btn btn-dark" @click="addToCart(product.id, quantities[product.id] || 1)">Add to Cart</button>
              <button v-else class="btn btn-dark" disabled>Add to Cart</button>
            </div>
          </div>
        </div>
      </div> 
    </div>
  </div>

</template>

<script>

import NavBar from '@/components/NavBar.vue';
import userMixin from '../mixins/userMixin';

export default {
  name: 'HomeView',
  components: {
    NavBar
  },
  mixins: [userMixin],
  data() {
    return {
      quantities: {},
      categories: [],
      searchQuery: ''
    }
  },
  computed: {
    filteredCategories() {
      const searchTerm = this.searchQuery.toLowerCase();
      return this.categories.map(category => {
        const filteredProducts = category.products.filter(product => 
          product.name.toLowerCase().includes(searchTerm)
        );
        return { ...category, products: filteredProducts };
      }).filter(category => category.products.length > 0);
    }
  },
  async created() {
    this.getCategories();
  },
  methods: {
    async getCategories() {
      const response = await fetch('http://localhost:5000/categories', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
      });
      const data = await response.json();
      this.categories = data;
    },
    async addToCart(productId, quantity) {
      const response = await fetch('http://localhost:5000/add-to-cart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + localStorage.getItem('access_token')
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: quantity
        })
      });
      const data = await response.json();
      if (!response.ok) {
        alert(data.error);
      }
      else {
        console.log(data.message);
        this.quantities = {};
      }
    }
  }
}
</script>
