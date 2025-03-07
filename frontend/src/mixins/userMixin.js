export default {
    data() {
        return {
            user: null,
            role: null,
            isLoggedIn: false
        }
    },
    async created() {
        await this.checkAuth();
    },
    methods: {
        async checkAuth() {
            const access_token = localStorage.getItem("access_token");
            if(!access_token){
                this.isLoggedIn = false;
                this.user = null;
                this.role = null;
                return;
            }
            try{
                this.user = await this.getUserInfo(access_token);
                console.log(this.user);
            }
            catch(e){
                this.user = null;
                this.role = null;
                this.isLoggedIn = false;
                console.log(e);
                return;
            }
        },
        async getUserInfo(access_token) {
            const response = await fetch("http://localhost:5000/getuserinfo", {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    "Authorization": "Bearer " + access_token
                }
            });
            const data = await response.json();
            if (!response.ok){
                console.log("Not logged in");
                return null;
            }
            else{
                console.log("Logged in");
                this.isLoggedIn = true;
                this.role = data.role;
                return data;
            }
        },
        async logout() {
            const response = await fetch("http://localhost:5000/logout", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + localStorage.getItem("access_token")
                }
            });
            const data = await response.json();
            if (!response.ok){
                alert(data.error)
            }
            else{
                console.log(data.message)
                localStorage.removeItem("access_token");
                this.user = null;
                this.role = null;
                this.isLoggedIn = false;
                // Redirecting to login page
                this.$router.push("/login");
            }
        }
    }
}