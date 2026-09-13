const logoutBtn = document.getElementById("logoutBtn");
const manageFiles = document.getElementById("manageFiles");
const manageUsers = document.getElementById("manageUsers");
const openSettings = document.getElementById("openSettings");

logoutBtn.addEventListener("click", () => {
    alert("Logout functionality will be connected to the backend later.");
});

manageFiles.addEventListener("click", () => {
    window.location.href = "../dashboard/index.html";
});

manageUsers.addEventListener("click", () => {
    alert("User management will be available after backend integration.");
});

openSettings.addEventListener("click", () => {
    window.location.href = "../settings/index.html";
});
