<script>
  let preference = $state("auto");
  let resolvedTheme = $state("light");

  $effect(() => {
    const savedPref = localStorage.getItem("theme-preference");
    if (savedPref === "light" || savedPref === "dark" || savedPref === "auto") {
      preference = savedPref;
    }
  });

  $effect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const updateResolvedTheme = () => {
      if (preference === "auto") {
        resolvedTheme = mediaQuery.matches ? "dark" : "light";
      } else {
        resolvedTheme = preference;
      }
    };

    updateResolvedTheme();

    document.documentElement.setAttribute("data-bs-theme", resolvedTheme);
    localStorage.setItem("theme-preference", preference);

    mediaQuery.addEventListener("change", updateResolvedTheme);

    return () => mediaQuery.removeEventListener("change", updateResolvedTheme);
  });

  function cyclePreference() {
    if (preference === "auto") {
      preference = "light";
    } else if (preference === "light") {
      preference = "dark";
    } else {
      preference = "auto";
    }
  }
</script>

<button
  class="btn {resolvedTheme === 'dark'
    ? 'btn-light'
    : 'btn-dark'} rounded-circle p-2 lh-1"
  onclick={cyclePreference}
  aria-label="Theme preference: {preference}"
  title="Theme: {preference}"
>
  {#if preference === "auto"}
    <i class="bi bi-circle-half fs-4"></i>
  {:else if preference === "light"}
    <i class="bi bi-sun-fill fs-4"></i>
  {:else}
    <i class="bi bi-moon-fill fs-4"></i>
  {/if}
</button>
