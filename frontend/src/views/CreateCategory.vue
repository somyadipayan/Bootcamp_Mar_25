<template>
    <NavBar/>
    <div class="container mt-5">
        <h2>Create Category</h2>
        <form @submit.prevent="createCategory">
            <div class="mb-3">
                <label for="name" class="form-label">Category Name</label>
                <input type="text" v-model="name" class="form-control" id="name">
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
            name: ''
        }
    },
    methods: {
        async createCategory() {
            const response = await fetch('http://localhost:5000/category', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                },
                body: JSON.stringify({
                    name: this.name
                })               
            })
            const data = await response.json()
            if (!response.ok) {
                alert(data.error)
            }
            else {
                console.log(data.message)
                // Redirect to all categories page
                this.$router.push('/all-categories')
            }
        }
    }
            
}
</script>