const menuButton = document.getElementById("menu-button");
const viewAllButton = document.getElementById("view-all");

const actionCards = document.querySelectorAll(".action-card");
const navItems = document.querySelectorAll(".nav-item");
const fileMenus = document.querySelectorAll(".file-menu");

/* Top menu */

menuButton.addEventListener("click", () => {
    alert("Navigation menu will be expanded here.");
});

/* Recent files */

viewAllButton.addEventListener("click", () => {
    window.location.href = "../search/index.html";
});

/* Quick actions */

actionCards.forEach((card) => {
    card.addEventListener("click", () => {
        const action = card.textContent.trim();

        if (action === "Files") {
            window.location.href = "../search/index.html";
            return;
        }

        if (action === "Search") {
            window.location.href = "../search/index.html";
            return;
        }

        if (action === "AI Assistant") {
            window.location.href = "../ai/index.html";
            return;
        }

        if (action === "Settings") {
            window.location.href = "../settings/index.html";
        }
    });
});

/* Bottom navigation */

navItems.forEach((item) => {
    item.addEventListener("click", () => {
        const section = item.querySelector("small").textContent;

        if (section === "Home") {
            window.location.href = "../dashboard/index.html";
            return;
        }

        if (section === "Files") {
            window.location.href = "../search/index.html";
            return;
        }

        if (section === "AI") {
            window.location.href = "../ai/index.html";
            return;
        }

        if (section === "Settings") {
            window.location.href = "../settings/index.html";
        }
    });
});

/* File options */

fileMenus.forEach((menu) => {
    menu.addEventListener("click", () => {
        const fileName = menu
            .closest(".file-item")
            .querySelector(".file-info strong")
            .textContent;

        alert(`Options for ${fileName} will be connected later.`);
    });
});
