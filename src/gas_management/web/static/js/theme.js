/* Applies the saved (or system-preferred) colour theme before first paint to
   avoid a flash of the wrong theme. Loaded synchronously in <head>. */
(function () {
  try {
    var saved = localStorage.getItem("gms-theme");
    var prefersDark =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    var theme = saved || (prefersDark ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", theme);
  } catch (e) {
    /* localStorage may be unavailable; fall back to the default light theme. */
  }
})();
