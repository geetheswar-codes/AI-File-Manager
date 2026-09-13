const searchInput = document.getElementById("search-input");
const clearSearch = document.getElementById("clear-search");
const fileList = document.getElementById("file-list");
const fileHeading = document.getElementById("file-heading");
const fileCount = document.getElementById("file-count");
const emptyMessage = document.getElementById("empty-message");
const backButton = document.getElementById("back-button");
const addButton = document.getElementById("add-button");

const filters = document.querySelectorAll(".filter");
const folderCards = document.querySelectorAll(".folder-card");
const fileMenus = document.querySelectorAll(".file-menu");
const navItems = document.querySelectorAll(".nav-item");

function updateFiles() {
    const query = searchInput.value.trim().toLowerCase();
    const activeFilter = document.querySelector(".filter.active").dataset.filter;

    const files = document.querySelectorAll(".file-item");
    let visibleCount = 0;

    files.forEach((file) => {
        const name = file.querySelector(".file-info strong").textContent.toLowerCase();
        const type = file.dataset.type;

        const matchesSearch = name.includes(query);
        const matchesFilter =
            activeFilter === "all" || type === activeFilter;

        const visible = matchesSearch && matchesFilter;

        file.hidden = !visible;

        if (visible) {
            visibleCount++;
        }
    });

    fileCount.textContent =
        `${visibleCount} ${visibleCount === 1 ? "file" : "files"}`;

    emptyMessage.hidden = visibleCount !== 0;

    clearSearch.hidden = query.length === 0;

    fileHeading.textContent = query ? "Search Results" : "Recent Files";
}

/* File View */

function applyFileView() {
    const view = localStorage.getItem("fileView") || "List";
    const isGrid = view === "Grid";

    fileList.classList.toggle("grid-view", isGrid);

    if (isGrid) {
        fileList.style.display = "grid";
        fileList.style.gridTemplateColumns = "repeat(2, minmax(0, 1fr))";
        fileList.style.gap = "12px";

        document.querySelectorAll(".file-item").forEach((file) => {
            file.style.display = "flex";
            file.style.flexDirection = "column";
            file.style.alignItems = "flex-start";
            file.style.justifyContent = "center";
            file.style.position = "relative";
            file.style.minHeight = "150px";
        });
    } else {
        fileList.style.display = "flex";
        fileList.style.flexDirection = "column";
        fileList.style.gap = "9px";

        document.querySelectorAll(".file-item").forEach((file) => {
            file.style.display = "flex";
            file.style.flexDirection = "row";
            file.style.alignItems = "center";
            file.style.justifyContent = "initial";
            file.style.position = "static";
            file.style.minHeight = "68px";
        });
    }
}

applyFileView();

searchInput.addEventListener("input", updateFiles);

clearSearch.addEventListener("click", () => {
    searchInput.value = "";
    searchInput.focus();
    updateFiles();
});

filters.forEach((filter) => {
    filter.addEventListener("click", () => {
        filters.forEach((item) => {
            item.classList.remove("active");
        });

        filter.classList.add("active");
        updateFiles();
    });
});

backButton.addEventListener("click", () => {
    window.location.href = "../dashboard/index.html";
});

addButton.addEventListener("click", () => {
    alert("File upload will be connected to the backend soon.");
});

folderCards.forEach((folder) => {
    folder.addEventListener("click", () => {
        const folderName = folder.querySelector("span:nth-child(2)").textContent;

        alert(`${folderName} folder browsing will be connected soon.`);
    });
});

fileMenus.forEach((menu) => {
    menu.addEventListener("click", () => {
        const fileName = menu
            .closest(".file-item")
            .querySelector(".file-info strong")
            .textContent;

        alert(`Options for ${fileName} will be connected soon.`);
    });
});

navItems.forEach((item) => {
    item.addEventListener("click", () => {
        const page = item.dataset.page;

        if (page === "dashboard") {
            window.location.href = "../dashboard/index.html";
            return;
        }

        if (page === "ai") {
            window.location.href = "../ai/index.html";
            return;
        }

        if (page === "settings") {
            window.location.href = "../settings/index.html";
        }
    });
});

updateFiles();
