<script setup lang="ts">
interface Props {
  title: string;
  subtitle?: string;
}

defineProps<Props>();
</script>

<template>
  <section class="section-panel">
    <header>
      <div>
        <h3>{{ title }}</h3>
        <p v-if="subtitle">{{ subtitle }}</p>
      </div>
      <div class="section-action"><slot name="action" /></div>
    </header>
    <div class="section-body">
      <slot />
    </div>
  </section>
</template>
