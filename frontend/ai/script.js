const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const messages = document.getElementById("messages");
const suggestions = document.getElementById("suggestions");
const newChatButton = document.getElementById("new-chat-button");
const backButton = document.getElementById("back-button");
const navItems = document.querySelectorAll(".nav-item");

const responses = {
    "find my largest files":
        "I can help find your largest files. Once connected to the backend, I'll scan your storage and sort files by size.",

    "find pdf files":
        "I found 1 PDF in the current demo data: document.pdf (2.4 MB).",

    "show my recent files":
        "Your recent files are document.pdf, report.xlsx, and project-image.jpg.",

    "help me organize my files":
        "I can help organize files by type, date, project, or other rules. Real file operations will be connected to the backend later."
};

function addMessage(text, sender) {
    const message = document.createElement("div");

    message.className = `message ${sender}`;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    if (sender === "assistant") {
        const label = document.createElement("span");
        label.className = "message-label";
        label.textContent = "AI Assistant";

        bubble.appendChild(label);
    }

    const content = document.createElement("span");
    content.textContent = text;

    bubble.appendChild(content);
    message.appendChild(bubble);
    messages.appendChild(message);

    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth"
    });
}

function showTyping() {
    const message = document.createElement("div");

    message.className = "message assistant";
    message.id = "typing-message";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    const label = document.createElement("span");
    label.className = "message-label";
    label.textContent = "AI Assistant";

    const typing = document.createElement("span");
    typing.className = "typing";

    typing.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    bubble.appendChild(label);
    bubble.appendChild(typing);
    message.appendChild(bubble);
    messages.appendChild(message);

    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth"
    });
}

function removeTyping() {
    const typingMessage = document.getElementById("typing-message");

    if (typingMessage) {
        typingMessage.remove();
    }
}

function getResponse(message) {
    const normalized = message.trim().toLowerCase();

    if (responses[normalized]) {
        return responses[normalized];
    }

    if (normalized.includes("pdf")) {
        return "I can search PDF files once the AI assistant is connected to the real file index.";
    }

    if (
        normalized.includes("large") ||
        normalized.includes("largest") ||
        normalized.includes("biggest")
    ) {
        return "I can identify your largest files after the backend file scanner is connected.";
    }

    if (
        normalized.includes("recent") ||
        normalized.includes("latest")
    ) {
        return "The demo currently has document.pdf, report.xlsx, and project-image.jpg as recent files.";
    }

    if (
        normalized.includes("organize") ||
        normalized.includes("sort")
    ) {
        return "I can help create an organization plan. Actual file movement will require the backend connection.";
    }

    return "I understand your request. The AI engine will be connected to the file manager backend in the next stage.";
}

function sendMessage(text) {
    const message = text.trim();

    if (!message) {
        return;
    }

    suggestions.hidden = true;
    chatInput.value = "";
    sendButton.disabled = true;

    addMessage(message, "user");
    showTyping();

    setTimeout(() => {
        removeTyping();
        addMessage(getResponse(message), "assistant");

        sendButton.disabled = false;
        chatInput.focus();
    }, 900);
}

chatForm.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage(chatInput.value);
});

suggestions.querySelectorAll(".suggestion").forEach((suggestion) => {
    suggestion.addEventListener("click", () => {
        sendMessage(suggestion.dataset.message);
    });
});

newChatButton.addEventListener("click", () => {
    messages.innerHTML = "";
    suggestions.hidden = false;
    chatInput.value = "";
    chatInput.focus();
});

backButton.addEventListener("click", () => {
    window.location.href = "../dashboard/index.html";
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

        if (page === "settings") {
            alert("Settings will be connected soon.");
        }
    });
});
