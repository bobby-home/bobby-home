/**
 * As I don't use a state manager, I decided to abstract the state management
 * in its own little class.
 * I don't use a state manager because it is... very straightforward.
 */
export class DialogManager {

  constructor(mounted) {
    this.mounted = mounted
  }

  open(dialog, validCallback, cancelCallback) {
    const defaultPayload = {
      validCallback: () => {
        this.close()
        validCallback()
      },
      cancelCallback: () => {
        this.close()
        if (cancelCallback) {
          cancelCallback()
        }
      }
    }

    this.mounted.$data.confirmDialog = {
      ...dialog, ...defaultPayload
    }
  }

  close() {
    this.mounted.$data.confirmDialog = null
  }
}
