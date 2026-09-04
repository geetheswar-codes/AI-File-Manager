const backButton = document.getElementById("back-button");
const viewSetting = document.getElementById("view-setting");
const securitySetting = document.getElementById("security-setting");

const navItems = document.querySelectorAll(".nav-item");

/* Back to dashboard */

backButton.addEventListener("click", () => {
    window.location.href = "../dashboard/index.html";
});

/* Default file view */

viewSetting.addEventListener("click", () => {
    if (viewSetting.textContent.trim() === "List") {
        viewSetting.textContent = "Grid";
    } else {
        viewSetting.textContent = "List";
    }
});

/* Account */

document.querySelector(".profile-card").addEventListener("click", () => {
    alert("Account settings will be connected to the backend later.");
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

        if (page === "settings") {
            return;
        }
    });
});

/* Settings feedback */

const settingInputs = document.querySelectorAll(
    '.switch input[type="checkbox"]'
);

settingInputs.forEach((input) => {
    input.addEventListener("change", () => {
        const settingName = input.id;

        console.log(
            `${settingName}: ${input.checked ? "enabled" : "disabled"}`
        );
    });
});
