/* Progressive enhancement for the Gas Management dashboard.
   Everything here is optional: the app works fully without JavaScript. */
(function () {
  "use strict";

  /* ---- Theme toggle ---------------------------------------------------- */
  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem("gms-theme", theme);
    } catch (e) {
      /* ignore */
    }
  }
  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var current =
        document.documentElement.getAttribute("data-theme") === "dark"
          ? "light"
          : "dark";
      setTheme(current);
    });
  });

  /* ---- Mobile navigation ---------------------------------------------- */
  document.querySelectorAll("[data-nav-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var nav = document.getElementById("primary-nav");
      var open = document.body.classList.toggle("nav-open");
      btn.setAttribute("aria-expanded", String(open));
      if (nav) nav.classList.toggle("is-open", open);
    });
  });

  /* ---- Top progress bar (loading state on navigation/submit) ---------- */
  var bar = document.getElementById("progress");
  function showProgress() {
    if (!bar) return;
    bar.classList.add("is-active");
  }
  window.addEventListener("beforeunload", showProgress);
  document.querySelectorAll("form").forEach(function (form) {
    form.addEventListener("submit", showProgress);
  });

  /* ---- Confirm destructive actions ------------------------------------ */
  document.querySelectorAll("[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.getAttribute("data-confirm"))) {
        e.preventDefault();
      }
    });
  });

  /* ---- Billing: show only the relevant litre fields ------------------- */
  var billing = document.querySelector("[data-billing]");
  if (billing) {
    var cngField = billing.querySelector("[data-cng-field]");
    var lpgField = billing.querySelector("[data-lpg-field]");
    function syncGasFields() {
      var type = (billing.querySelector('input[name="gas_type"]:checked') || {})
        .value;
      if (cngField) cngField.hidden = type === "LPG";
      if (lpgField) lpgField.hidden = type === "CNG";
    }
    billing.querySelectorAll('input[name="gas_type"]').forEach(function (r) {
      r.addEventListener("change", syncGasFields);
    });
    syncGasFields();
  }

  /* ---- Live customer search with skeleton loaders --------------------- */
  var searchForm = document.querySelector("[data-search]");
  var results = document.querySelector("[data-results]");
  if (searchForm && results && window.fetch) {
    var input = searchForm.querySelector('input[name="q"]');
    var timer = null;

    function skeleton() {
      var rows = "";
      for (var i = 0; i < 5; i++) {
        rows +=
          '<div class="skeleton-row"><span class="skeleton"></span>' +
          '<span class="skeleton"></span><span class="skeleton"></span></div>';
      }
      results.innerHTML = '<div class="skeleton-list">' + rows + "</div>";
    }

    function run(q) {
      skeleton();
      fetch("/customers?partial=1&q=" + encodeURIComponent(q), {
        headers: { "X-Requested-With": "fetch" },
      })
        .then(function (r) {
          return r.text();
        })
        .then(function (html) {
          results.innerHTML = html;
        })
        .catch(function () {
          results.innerHTML =
            '<div class="empty"><p>Could not load results. Please retry.</p></div>';
        });
    }

    searchForm.addEventListener("submit", function (e) {
      e.preventDefault();
      run(input.value.trim());
    });
    input.addEventListener("input", function () {
      window.clearTimeout(timer);
      timer = window.setTimeout(function () {
        run(input.value.trim());
      }, 280);
    });
  }
})();
