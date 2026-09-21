const form = document.getElementById("register-form");
const username = document.getElementById("username");
const email = document.getElementById("email");
const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirm-password");
const registerButton = document.getElementById("register-button");
const buttonText = document.getElementById("button-text");
const registerMessage = document.getElementById("register-message");
const togglePassword = document.getElementById("toggle-password");
const toggleConfirmPassword = document.getElementById("toggle-confirm-password");

const API_BASE_URL = "http://127.0.0.1:8000";

function toggleVisibility(input, button) {
    const isPassword = input.type === "password";

    input.type = isPassword ? "text" : "password";
    button.textContent = isPassword ? "Hide" : "Show";
    button.setAttribute(
        "aria-label",
        isPassword ? "Hide password" : "Show password"
    );
}

togglePassword.addEventListener("click", () => {
    toggleVisibility(password, togglePassword);
});

toggleConfirmPassword.addEventListener("click", () => {
    toggleVisibility(confirmPassword, toggleConfirmPassword);
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const userName = username.value.trim();
    const userEmail = email.value.trim();
    const userPassword = password.value;
    const confirmation = confirmPassword.value;

    registerMessage.textContent = "";

    if (userPassword !== confirmation) {
        registerMessage.textContent = "Passwords do not match.";
        return;
    }

    registerButton.disabled = true;
    buttonText.textContent = "Creating account...";

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: userName,
                email: userEmail,
                password: userPassword
            })
        });

        const data = await response.json();

        if (!response.ok) {
            let message = "Registration failed.";

            if (Array.isArray(data.detail)) {
                message = data.detail
                    .map((error) => error.msg)
                    .join(" ");
            } else if (data.detail) {
                message = data.detail;
            }

            throw new Error(message);
        }

        registerMessage.textContent = "Account created. Redirecting to sign in...";

        setTimeout(() => {
            window.location.href = "../login/index.html";
        }, 800);

    } catch (error) {
        console.error("Registration error:", error);

        registerMessage.textContent =
            error.message || "Unable to connect to the backend.";

        registerButton.disabled = false;
        buttonText.textContent = "Create account";
    }
});
