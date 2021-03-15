/**
 *
 * @returns {string}
 */
function getSavedTheme() {
    return window.localStorage.getItem('theme')
}

/**
 *
 * @param {string} themeName
 */
function saveTheme(themeName) {
    window.localStorage.setItem('theme', themeName)
}


export class ThemeChoice extends HTMLElement {
    connectedCallback () {
        this.classList.add('theme-choice')
        this.innerHTML = `
        <input type="checkbox" is="input-switch" id="theme-switcher" aria-label="Changer de thème">
        <label for="theme-switcher">
            <svg class="icon icon-moon">
                <use xlink:href="${window.SPRITE}#moon"></use>
              </svg>
              <svg class="icon icon-sun">
                <use xlink:href="${window.SPRITE}#sun"></use>
              </svg>
        </label>`

        const input = this.querySelector('input')
        input.addEventListener('change', e => {
            const themeToRemove = e.currentTarget.checked ? 'light' : 'dark'
            const themeToAdd = e.currentTarget.checked ? 'dark' : 'light'
            document.body.classList.add(`theme-${themeToAdd}`)
            document.body.classList.remove(`theme-${themeToRemove}`)

            saveTheme(themeToAdd)
        })

        const savedTheme = getSavedTheme()
        if (savedTheme) {
            document.body.classList.add(`theme-${savedTheme}`)
            input.checked = savedTheme === 'dark'
        } else {
            input.checked = window.matchMedia('(prefers-color-scheme: dark)').matches
        }
    }
}
