const backButton = document.getElementById("back-button");
const navItems = document.querySelectorAll(".nav-item");

backButton.addEventListener("click", () => {
    window.location.href = "../settings/index.html";
});

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
            window.location.href = "../settings/index.html";
        }
    });
});

document.querySelectorAll(".profile-action").forEach((action) => {
    action.addEventListener("click", () => {
        const title = action.querySelector("strong").textContent;

        alert(`${title} will be connected later.`);
    });
});
