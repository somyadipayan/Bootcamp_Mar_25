<template>
    <NavBar />
    <div class="container mt-5">
        <h2>All Categories</h2>
        <div class="row">
            <div v-for="category in categories" class="card mb-3 mt-3 col-md-3">
                <div class="card-body">
                    <h5 class="card-title">{{ category.id }}. {{ category.name }}</h5>
                    <p class="card-text">{{ category.products.length }} Products</p>
                    <div class="btn-group">
                        <a href="#" class="btn btn-dark">View Products</a>
                        <router-link :to="`/update-category/${category.id}`" v-if="role == 'admin' || role == 'manager'" class="btn btn-dark">Edit</router-link>
                        <button v-if="role == 'admin' || role == 'manager'" class="btn btn-dark" @click="deleteCategory(category.id)">Delete</button>
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
    name: "AllCategories",
    components: {
        NavBar
    },
    mixins: [userMixin],
    data() {
        return {
            categories: []
        }
    },
    created() {
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
        async deleteCategory(id) {
            const response = await fetch(`http://localhost:5000/category/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                },
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.error);
            }
            else {
                console.log(data.message);
                this.getCategories();
            }
        }
    }
}

</script>