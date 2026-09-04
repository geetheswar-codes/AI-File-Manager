const form = document.getElementById("login-form");
const username = document.getElementById("username");
const password = document.getElementById("password");
const loginButton = document.getElementById("login-button");
const buttonText = document.getElementById("button-text");
const loginMessage = document.getElementById("login-message");
const togglePassword = document.getElementById("toggle-password");

togglePassword.addEventListener("click", () => {
    const isPassword = password.type === "password";

    password.type = isPassword ? "text" : "password";
    togglePassword.textContent = isPassword ? "Hide" : "Show";

    togglePassword.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
    );
});

form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (!username.value.trim() || !password.value) {
        loginMessage.textContent = "Please enter your username and password.";
        return;
    }

    loginMessage.textContent = "";
    loginButton.disabled = true;
    buttonText.textContent = "Signing in...";

    setTimeout(() => {
        window.location.href = "../dashboard/index.html";
    }, 800);
});
