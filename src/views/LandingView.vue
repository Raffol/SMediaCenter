<script setup>
import HeroSection from '@/components/landing/HeroSection.vue'
import AboutSection from '@/components/landing/AboutSection.vue'
import PostsSection from '@/components/landing/PostsSection.vue'
import ServicesSection from '@/components/landing/ServicesSection.vue'
import MembersSection from '@/components/landing/MembersSection.vue'
import PriceSection from '@/components/landing/PriceSection.vue'
import RequestFormSection from '@/components/landing/RequestFormSection.vue'
</script>

<template>
  <!--
    Порядок секций: фото → чистый фон → фото. Ритм из второго варианта
    макета, где фотография была не под каждым блоком. Когда фон везде,
    глазу негде отдохнуть и ни один блок не выделяется.

    «Последние работы» стоят сразу после «Кто мы»: сначала показываем,
    что умеем, потом называем цену.
  -->
  <HeroSection />
  <AboutSection />
  <PostsSection />
  <ServicesSection />
  <MembersSection />
  <PriceSection />
  <RequestFormSection />
</template>
