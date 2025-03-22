<template>
    <NavBar />
    <div class="container mt-5">
        <h2>My Orders</h2>
        <div v-if="orders.length === 0" class="alert alert-info mt-3">
            No orders found
        </div>

        <div v-else class="mt-4">
            <div v-for="order in orders" :key="order.id" class="card mb-4">
                <div class="card-header bg-light d-flex justify-content-between">
                    <div>
                        <h5 class="mb-0">Order #{{ order.id }}</h5>
                        <small class="text-muted">Date: {{ formatDate(order.date) }}</small>
                    </div>
                    <div>
                        <span class="badge bg-primary">Total: ₹{{ order.total }}</span>
                    </div>
                </div>
                
                <div class="card-body">
                    <div class="list-group">
                        <div v-for="(item, index) in order.items" :key="index" 
                             class="list-group-item border-0">
                            <div class="row align-items-center">
                                <div class="col-md-6">
                                    <h6 class="mb-1">{{ item.name }}</h6>
                                    <small class="text-muted">Product ID: {{ item.product_id }}</small>
                                </div>
                                <div class="col-md-3">
                                    <span>Quantity: {{ item.quantity }}</span>
                                </div>
                                <div class="col-md-3 text-end">
                                    <span>₹{{ item.subtotal }}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-3">
            <router-link to="/" class="btn btn-outline-secondary">
                <i class="bi bi-arrow-left"></i> Back to Shopping
            </router-link>
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import userMixin from '../mixins/userMixin';

export default {
    name: "UserOrders",
    components: {
        NavBar
    },
    mixins: [userMixin],
    data() {
        return {
            orders: []
        }
    },
    created() {
        this.getOrders();
    },
    methods: {
        async getOrders() {
            try {
                const response = await fetch('http://localhost:5000/get-orders', {
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });

                if (!response.ok) throw new Error('Failed to fetch orders');
                
                const data = await response.json();
                this.orders = data.orders;
            } catch (error) {
                alert(error.message);
            }
        },
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-IN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
}
</script>

<style scoped>
.card-header {
    background-color: #f8f9fa !important;
}
.list-group-item {
    padding: 1rem 0;
    border-bottom: 1px solid rgba(0,0,0,.125);
}
.list-group-item:last-child {
    border-bottom: 0;
}
.badge {
    font-size: 1rem;
    padding: 0.5em 0.75em;
}
</style>