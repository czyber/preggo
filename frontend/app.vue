<template>
  <div>
    <Head>
      <Meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no" />
    </Head>
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
    <Toast />
    <CelebrationAnimation />
  </div>
</template>

<script setup>
// Add global styles to prevent horizontal overflow
useHead({
  style: [{
    children: `
      html, body {
        overflow-x: hidden;
        width: 100%;
        max-width: 100vw;
      }
    `
  }]
})
</script>