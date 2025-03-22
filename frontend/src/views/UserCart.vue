<template>
    <NavBar />
    <div class="container mt-5">
        <h2>Your Shopping Cart</h2>
        <div v-if="cartItems.length === 0" class="alert alert-info mt-3">
            Your cart is empty
        </div>
        
        <div v-else>
            <div class="card mt-3">
                <div class="card-body">
                    <div class="list-group">
                        <div v-for="item in cartItems" :key="item.item_id" class="list-group-item">
                            <div class="row align-items-center">
                                <div class="col-md-4">
                                    <h5>{{ item.product_name }}</h5>
                                    <p class="mb-0">₹{{ item.unit_price }} per {{ item.unit }}</p>
                                </div>
                                <div class="col-md-4">
                                    <div class="input-group">
                                        <input 
                                            type="number" 
                                            class="form-control"
                                            v-model.number="item.quantity"
                                            min="1"
                                            @change="updateQuantity(item.item_id, item.quantity)"
                                        >
                                        <button 
                                            class="btn btn-outline-danger"
                                            @click="removeItem(item.item_id)"
                                        >
                                            Remove
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-4 text-end">
                                    <p class="mb-0">Total: ₹{{ item.total }}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <div class="row">
                        <div class="col-md-6">
                            <h4>Total Amount: ₹{{ totalAmount }}</h4>
                        </div>
                        <div class="col-md-6 text-end">
                            <button 
                                class="btn btn-success btn-lg"
                                @click="placeOrder"
                            >
                                Place Order
                            </button>
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
    name: "ShoppingCart",
    components: {
        NavBar
    },
    mixins: [userMixin],
    data() {
        return {
            cartItems: [],
            totalAmount: 0
        }
    },
    created() {
        this.getCart();
    },
    methods: {
        async getCart() {
            try {
                const response = await fetch('http://localhost:5000/view-cart', {
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });
                
                if (!response.ok) throw new Error('Failed to fetch cart');
                
                const data = await response.json();
                this.cartItems = data.cart_items;
                this.totalAmount = data.total_amount;
            } catch (error) {
                alert(error.message);
            }
        },
        async updateQuantity(itemId, newQuantity) {
            if (newQuantity < 1) return;
            
            try {
                const response = await fetch(`http://localhost:5000/update-cart/${itemId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    body: JSON.stringify({ quantity: newQuantity })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error);
                }

                await this.getCart(); // Refresh cart data
            } catch (error) {
                alert(error.message);
                this.getCart(); // Reset to actual values
            }
        },
        async removeItem(itemId) {
            if (!confirm('Are you sure you want to remove this item?')) return;
            
            try {
                const response = await fetch(`http://localhost:5000/remove-from-cart/${itemId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });

                if (!response.ok) throw new Error('Failed to remove item');
                
                this.cartItems = this.cartItems.filter(item => item.item_id !== itemId);
                this.getCart(); // Refresh total amount
            } catch (error) {
                alert(error.message);
            }
        },
        async placeOrder() {
            if (!confirm('Confirm placing this order?')) return;
            
            try {
                const response = await fetch('http://localhost:5000/place-order', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error);
                }

                alert('Order placed successfully!');
                this.$router.push('/orders');
            } catch (error) {
                alert(error.message);
            }
        }
    }
}
</script>

<style scoped>
.input-group {
    max-width: 300px;
}
.list-group-item {
    padding: 1.5rem;
}
.card-footer {
    background-color: #f8f9fa;
}
</style>