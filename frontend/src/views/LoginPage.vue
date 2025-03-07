<template>
    <NavBar/>
    <div class="container mt-5" style="text-align: center;">
        <div class="card" style="padding: 50px;">
        <h2 class="card-title">Login Here</h2>
        <form class="mt-3" @submit.prevent="login">
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" v-model = "username" class="form-control" id="username" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" v-model = "password" class="form-control" id="password">
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
export default {
    data() {
        return {
            username: "",
            password: ""
        }
    },
    components: {
        NavBar
    },

    methods: {
        async login() {
            const response = await fetch("http://localhost:5000/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: this.username,
                    password: this.password
                })
            })
            const data = await response.json()
            if (!response.ok){
                alert(data.error)
            }
            else{
                console.log(data.message)
                console.log(data.access_token)
                localStorage.setItem("access_token", data.access_token)
                const token = localStorage.getItem("access_token")
                console.log("Here is access_token from my local storage",token)
                // Redirecting to home page
                this.$router.push("/") 
            }
        }
    }

}

</script>   