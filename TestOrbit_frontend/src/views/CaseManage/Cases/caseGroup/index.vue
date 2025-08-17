
<template>
    <div class="container">
    <!--顶部操作框-->
    <div class="top">
        <Head />
    </div>
    <!----用例组展示框-->
    <div class="case-group">
        <ListDetail />
    </div>
</div>
</template>

<script setup>
import { ref } from 'vue'
import Head from './head.vue';
import ListDetail from './ListDetail/index.vue';

</script>