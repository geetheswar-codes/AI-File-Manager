const menuButton = document.getElementById("menu-button");
const viewAllButton = document.getElementById("view-all");

const actionCards = document.querySelectorAll(".action-card");
const navItems = document.querySelectorAll(".nav-item");
const fileMenus = document.querySelectorAll(".file-menu");

menuButton.addEventListener("click", () => {
    alert("Menu will be connected to navigation soon.");
});

viewAllButton.addEventListener("click", () => {
    alert("File manager will be connected here soon.");
});

actionCards.forEach((card) => {
    card.addEventListener("click", () => {
        const action = card.textContent.trim();

        alert(`${action} section will be connected soon.`);
    });
});

navItems.forEach((item) => {
    item.addEventListener("click", () => {
        navItems.forEach((nav) => nav.classList.remove("active"));
        item.classList.add("active");

        const section = item.querySelector("small").textContent;

        if (section !== "Home") {
            alert(`${section} section will be connected soon.`);
        }
    });
});

fileMenus.forEach((menu) => {
    menu.addEventListener("click", () => {
        alert("File options will be connected soon.");
    });
});
