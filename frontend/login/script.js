const form = document.getElementById("login-form");
const username = document.getElementById("username");
const password = document.getElementById("password");
const loginButton = document.getElementById("login-button");
const buttonText = document.getElementById("button-text");
const loginMessage = document.getElementById("login-message");
const togglePassword = document.getElementById("toggle-password");

const API_BASE_URL = "http://127.0.0.1:8000";

togglePassword.addEventListener("click", () => {
    const isPassword = password.type === "password";

    password.type = isPassword ? "text" : "password";
    togglePassword.textContent = isPassword ? "Hide" : "Show";

    togglePassword.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
    );
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = username.value.trim();
    const userPassword = password.value;

    if (!email || !userPassword) {
        loginMessage.textContent = "Please enter your email and password.";
        return;
    }

    loginMessage.textContent = "";
    loginButton.disabled = true;
    buttonText.textContent = "Signing in...";

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: userPassword
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Login failed.");
        }

        localStorage.setItem("access_token", data.access_token);

        window.location.href = "../dashboard/index.html";

    } catch (error) {
        console.error("Login error:", error);

        loginMessage.textContent =
            error.message || "Unable to connect to the backend.";

        loginButton.disabled = false;
        buttonText.textContent = "Sign in";
    }
});
