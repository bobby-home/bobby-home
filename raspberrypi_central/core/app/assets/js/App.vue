<template>
  <transition name="dialog">
    <confirm-action-dialog v-if="isDialog" v-bind="confirmDialog" />
  </transition>
</template>

<script>
import ConfirmActionDialog from "./components/ConfirmActionDialog.vue"

export default {
  name: 'App',
  components: {
    ConfirmActionDialog,
  },

  data() {
    return {
      confirmDialog: null
    }
  },

  computed: {
    isDialog() {
      return this.confirmDialog !== null
    }
  }

}
</script>
