<template>
    <NavBar/>
    <div class="container mt-5">
        <h2>Update Product</h2>
        <form @submit.prevent="updateProduct">
            <div class="mb-3">
                <label for="name" class="form-label">Product Name</label>
                <input type="text" v-model="name" class="form-control" id="name">
            </div>
            <div class="mb-3">
                <label for="unit" class="form-label">Unit</label>
                <input type="text" v-model="unit" class="form-control" id="unit">
            </div>
            <div class="mb-3">
                <label for="price" class="form-label">Price</label>
                <input type="number" v-model="price" class="form-control" id="price">
            </div>
            <div class="mb-3">
                <label for="quantity" class="form-label">Quantity</label>
                <input type="number" v-model="quantity" class="form-control" id="quantity">
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
export default {
    components: {
        NavBar
    },
    data() {
        return {
            name: '',
            unit: '',
            price: 0,
            quantity: 0
        }
    },
    created() {
        const id = this.$route.params.id;
        this.getProduct(id);
    },
    methods: {
        async getProduct(id) {
            const response = await fetch(`http://localhost:5000/product/${id}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
            });
            const data = await response.json();
            this.name = data.name;
            this.unit = data.unit;
            this.price = data.price;
            this.quantity = data.quantity;
        },
        async updateProduct() {
            const id = this.$route.params.id
            const response = await fetch(`http://localhost:5000/product/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                },
                body: JSON.stringify({
                    name: this.name,
                    unit: this.unit,
                    price: this.price,
                    quantity: this.quantity,
            })
            })
            const data = await response.json()
            if (!response.ok) {
                alert(data.error)
            }
            else {
                console.log(data.message)
                // Redirect to all products page
                this.$router.push('/')
            }
        }
    }
}
</script>