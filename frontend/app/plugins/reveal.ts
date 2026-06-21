export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('reveal', {
    mounted(el, binding) {
      // Add base reveal class
      el.classList.add('reveal-on-scroll')

      // Support custom delays (e.g. v-reveal="150")
      let delayMs = 0
      if (typeof binding.value === 'number') {
        delayMs = binding.value
      } else if (binding.value && typeof binding.value === 'object') {
        delayMs = binding.value.delay || 0
      }

      if (delayMs > 0) {
        el.style.transitionDelay = `${delayMs}ms`
      }

      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            el.classList.add('in-view')
            observer.unobserve(el) // Only animate once
          }
        })
      }, {
        threshold: 0.05,
        rootMargin: '0px 0px -40px 0px' // Trigger slightly before entering to feel smooth
      })

      observer.observe(el)
      el._revealObserver = observer
    },
    unmounted(el) {
      if (el._revealObserver) {
        el._revealObserver.disconnect()
      }
    }
  })
})
