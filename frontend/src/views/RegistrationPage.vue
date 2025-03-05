<template>
    <div class="container mt-5" style="text-align: center;">
        <div class="card" style="padding: 50px;">
        <h2 class="card-title">Registration Page</h2>
        <form class="mt-3" @submit.prevent="register">
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" v-model = "username" class="form-control" id="username" required>
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" v-model = "email" class="form-control" id="email" required>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" v-model = "password" class="form-control" id="password">
            </div>
            <div class="mb-3 form-check" style="text-align: left;">
                <input v-model = "isManager" type="checkbox" class="form-check-input" id="isManager">
                <label class="form-check-label" for="isManager">Want to register as Manager?</label>
            </div>
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
        </div>
    </div>
</template>

<script>

export default {
    name: "RegistrationPage",
    data() {
        return {
            username: "",
            email: "",
            password: "",
            isManager: false
        }
    },
    methods: {
        async register() {
            const response = await fetch("http://localhost:5000/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: this.username,
                    email: this.email,
                    password: this.password,
                    role: this.isManager ? "manager" : "user"
                })
            })
            const data = await response.json()
            if (!response.ok){
                alert(data.error)
            }
            else{
                console.log(data.message)
                // Redirecting to login page
                this.$router.push("/") // Change to Login page once ready
            }

        }
    }
}
</script>


<style scoped></style>