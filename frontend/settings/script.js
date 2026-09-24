const backButton = document.getElementById("back-button");
const viewSetting = document.getElementById("view-setting");
const securitySetting = document.getElementById("security-setting");
const darkMode = document.getElementById("dark-mode");

const navItems = document.querySelectorAll(".nav-item");

/* Dark Mode */

function applyThemePreference() {
    const isDark = localStorage.getItem("darkMode") !== "false";
    darkMode.checked = isDark;
}

darkMode.addEventListener("change", () => {
    localStorage.setItem("darkMode", darkMode.checked);

    document.body.classList.toggle("light-mode", !darkMode.checked);
});

applyThemePreference();

/* Back to dashboard */

backButton.addEventListener("click", () => {
    window.location.href = "../dashboard/index.html";
});

/* Default file view */

function applyFileView() {
    const view = localStorage.getItem("fileView") || "List";
    viewSetting.textContent = view;
}

viewSetting.addEventListener("click", () => {
    const currentView = localStorage.getItem("fileView") || "List";
    const newView = currentView === "List" ? "Grid" : "List";

    localStorage.setItem("fileView", newView);
    applyFileView();
});

applyFileView();

/* Account */

document.querySelector(".profile-card").addEventListener("click", () => {
    window.location.href = "../profile/index.html";
});

/* Security */

securitySetting.addEventListener("click", () => {
    alert("Security and privacy settings will be connected later.");
});

/* Navigation */

navItems.forEach((item) => {
    item.addEventListener("click", () => {
        const page = item.dataset.page;

        if (page === "dashboard") {
            window.location.href = "../dashboard/index.html";
            return;
        }

        if (page === "files") {
            window.location.href = "../search/index.html";
            return;
        }

        if (page === "ai") {
            window.location.href = "../ai/index.html";
            return;
        }

        if (page === "profile") {
            window.location.href = "../profile/index.html";
            return;
        }

        if (page === "settings") {
            return;
        }
    });
});

/* Other settings */

const settingInputs = document.querySelectorAll(
    '.switch input[type="checkbox"]:not(#dark-mode)'
);

settingInputs.forEach((input) => {
    const savedValue = localStorage.getItem(input.id);

    if (savedValue !== null) {
        input.checked = savedValue === "true";
    }

    input.addEventListener("change", () => {
        localStorage.setItem(input.id, input.checked);
    });
});
