/* Shared AI File Manager Theme */

(function () {
    const isDark = localStorage.getItem("darkMode") !== "false";

    document.body.classList.toggle("light-mode", !isDark);
})();
