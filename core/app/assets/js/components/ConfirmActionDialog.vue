<template>
  <div class="dialog-popup" tabindex="0" @keydown.esc="onCancel" @click="onCancel">
    <div class="dialog-box box" @click.stop>
      <div class="dialog-box-body">

        <div class="dialog-icon">
          <svg-icon class="dialog-icon-svg" name="exclamation" />
        </div>

        <div class="copy variant--content dialog-content">
          <p class="h5">{{ title }}</p>
          <p>
            {{ content }}
          </p>
        </div>
        <div class="dialog-box-actions flex">
          <button class="btn" @click="onValidate">{{ validText }}</button>
          <button class="btn btn-transparent" @click="onCancel">{{ cancelText }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SvgIcon from "./SvgIcon.vue"

export default {
  name: "ConfirmActionDialog",
  components: {
    SvgIcon
  },
  props: {
    title: String,
    content: String,

    validText: {
      type: String,
      default: 'Continue'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },

    cancelCallback: {
      type: Function,
      required: true
    },
    validCallback: {
      type: Function,
      required: true
    }
  },

  methods: {
    onCancel() {
        this.cancelCallback()
    },

    onValidate() {
      this.validCallback()
    }
  },

  mounted() {
    this.$el.focus()
  }
}
</script>

<style lang="scss" scoped>
@import '../../css/helpers/_space.scss';
@import "../../css/tools/_responsive.scss";

/**
  Animation on mobile: from bottom to "top" with some fadeout.
  Animation on desktop: a zoom/in and out like here: https://tailwindui.com/components/application-ui/overlays/modals
 */

.box {
  --tw-ring-shadow: 0 0 #0000;
  --tw-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  box-shadow: var(0 0 #0000, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}

.dialog-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;

  &::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    z-index: -1;
  }

  z-index: 100;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.dialog-box-body {
  display: grid;
  padding: space(3) space(3) 0;
}

.dialog-box {
  width: 600px;
  background-color: var(--background-light);
}

.dialog-icon {
  place-self: center;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgb(254, 226, 226);
  color: rgb(220, 38, 38);
  width: 40px;
  height: 40px;
  border-radius: 100%;
  margin-bottom: space(2);
}

.dialog-icon-svg {
  height: 24px;
  width: 24px;
}

.dialog-content {
  text-align: center;
}

.dialog-box-actions {
  padding: space(2) space(0);
  flex-direction: column;

  button {
    padding: space(1);
  }

  > button:not(:first-of-type) {
    margin-left: space(2);
  }
}

@include emix-breakpoint($small) {
  .dialog-popup {
    align-items: center;
  }
  .dialog-content {
    text-align: left;
  }

  .dialog-icon {
      margin-right: space(2);
      margin-bottom: 0;
      place-self: start;
  }

  .dialog-box-body {
      grid-template-columns: repeat(2, auto);
  }

  .dialog-box-actions {
    flex-direction: row;
    grid-column: 2 / span 2;
  }
}

/**
  Animations
 */

.dialog-enter-active {
  &, .dialog-box {
    transition: all var(--enterTime);
    transition-timing-function: var(--enterTimingFunction);
  }

  &, &::after {
    transition: all var(--enterTime);
    transition-timing-function: var(--enterTimingFunction);
  }
}

.dialog-leave-active {
  &, .dialog-box {
    transition: all var(--leaveTime);
    transition-timing-function: var(--leaveTimingFunction);
  }

  &::after {
    transition: all var(--leaveTime);
    transition-timing-function: var(--leaveTimingFunction);
  }

}

.dialog-enter-from,
.dialog-leave-to {

  &::after {
    opacity: 0;
  }

  .dialog-box {
    transform: translateY(100%);
  }

}

@include emix-breakpoint($small) {
  .dialog-enter-from,
  .dialog-leave-to {
    .dialog-box {
      transform: scale3d(0.95, 0.95, 1);
    }
  }
}

</style>
