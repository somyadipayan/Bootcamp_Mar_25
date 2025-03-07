<template>
  <NavBar/>
  <div class="home">
    <h1 v-if="user">Welcome, {{user.username}}!</h1>
    <img alt="Vue logo" src="../assets/logo.png">
    <HelloWorld msg="Welcome to Bootcamp"/>
  </div>
</template>

<script>
// @ is an alias to /src
import HelloWorld from '@/components/HelloWorld.vue'
import NavBar from '@/components/NavBar.vue';
import userMixin from '../mixins/userMixin';

export default {
  name: 'HomeView',
  components: {
    HelloWorld,
    NavBar
  },
  mixins: [userMixin]
}
</script>
