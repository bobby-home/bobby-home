<template>
  <div class="alert-block"> <!-- I need a root element http://stackoverflow.com/a/39558146 -->

    <transition-group
        name="alert"
    >
      <div
          v-for="(alert, index) in alerts" :key="index"
          class="alert"
          @click="removeAlert(alert)">

        <div class="alert-bubble">
            <span
                class="alert-bubble--type"
                :class="[bubbleTypeClass(alert)]"></span>
        </div>

        <div class="copy__body flex items-center">
          {{ alert.message }}
        </div>

      </div>

    </transition-group>

  </div>

</template>

<script>
import './_alerts.scss' // Je dois le mettre ici, la balise <style> me retourne une CssSyntaxError (pb incompréhensible...)

export default {
  props: {
    alerts: { type: Array, required: true }
  },

  methods: {
    hide(alert) {
      console.log('hide')
    },

    removeAlert(alert) {
      this.$parent.removeAlert(alert)
    },

    bubbleTypeClass (alert) {
      return `alert-bubble--${alert.type}`
    }

  },
}
</script>
