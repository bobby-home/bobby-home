<template>
    <svg :class="className">
      <use :xlink:href="href"></use>
    </svg>
</template>

<script>
export default {
  name: "SvgIcon",
  props: {
    name: String
  },
  computed: {
    className() {
      return `icon icon-${this.name}`
    },

    href() {
      return `/public/svg/sprite.svg#${this.name}`
    }
  }
}
</script>

<style scoped>

</style>
