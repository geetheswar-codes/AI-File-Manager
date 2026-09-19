const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const messages = document.getElementById("messages");
const suggestions = document.getElementById("suggestions");
const newChatButton = document.getElementById("new-chat-button");
const backButton = document.getElementById("back-button");
const navItems = document.querySelectorAll(".nav-item");

const API_BASE_URL = "http://127.0.0.1:8000";

let userFiles = [];
let isLoading = false;


function getAccessToken() {
    return localStorage.getItem("access_token");
}


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


async function loadUserFiles() {
    const token = getAccessToken();

    if (!token) {
        addMessage(
            "You are not signed in. Please sign in first.",
            "assistant"
        );
        return false;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/files/`,
            {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            }
        );

        const data = await response.json();

        if (response.status === 401) {
            localStorage.removeItem("access_token");

            addMessage(
                "Your session has expired. Please sign in again.",
                "assistant"
            );

            return false;
        }

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to load your files."
            );
        }

        userFiles = Array.isArray(data.files)
            ? data.files
            : [];

        return true;

    } catch (error) {
        console.error("File loading error:", error);

        addMessage(
            "I couldn't connect to the file manager backend. Make sure the backend is running.",
            "assistant"
        );

        return false;
    }
}


async function scanFile(file) {
    const token = getAccessToken();

    if (!token) {
        throw new Error("You are not signed in.");
    }

    const response = await fetch(
        `${API_BASE_URL}/ai/scan/${file.id}`,
        {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );

    const data = await response.json();

    if (response.status === 401) {
        localStorage.removeItem("access_token");
        throw new Error(
            "Your session has expired. Please sign in again."
        );
    }

    if (!response.ok) {
        throw new Error(
            data.detail || "AI scan failed."
        );
    }

    return data;
}


function formatBytes(bytes) {
    if (!Number.isFinite(bytes) || bytes <= 0) {
        return "0 B";
    }

    const units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ];

    const exponent = Math.min(
        Math.floor(Math.log(bytes) / Math.log(1024)),
        units.length - 1
    );

    const value = bytes / Math.pow(1024, exponent);

    return `${value.toFixed(value >= 10 || exponent === 0 ? 0 : 1)} ${units[exponent]}`;
}


function getLargestFile() {
    if (!userFiles.length) {
        return null;
    }

    return [...userFiles]
        .sort(
            (a, b) =>
                (b.file_size || 0) -
                (a.file_size || 0)
        )[0];
}


function getPdfFiles() {
    return userFiles.filter((file) => {
        const filename = String(file.filename || "").toLowerCase();
        const fileType = String(file.file_type || "").toLowerCase();

        return (
            filename.endsWith(".pdf") ||
            fileType === "application/pdf"
        );
    });
}


function getRecentFiles() {
    return [...userFiles]
        .sort((a, b) => {
            const dateA = new Date(
                a.created_at ||
                a.updated_at ||
                a.modified_time ||
                0
            );

            const dateB = new Date(
                b.created_at ||
                b.updated_at ||
                b.modified_time ||
                0
            );

            return dateB - dateA;
        })
        .slice(0, 5);
}


function formatFileList(files) {
    if (!files.length) {
        return "I couldn't find any matching files.";
    }

    return files
        .map((file) => {
            const name = file.filename || "Unnamed file";
            const size = formatBytes(file.file_size || 0);

            return `• ${name} — ${size}`;
        })
        .join("\n");
}


function formatRecommendations(recommendations) {
    if (!recommendations || !recommendations.length) {
        return "";
    }

    const lines = recommendations
        .slice(0, 5)
        .map((recommendation) => {
            const confidence =
                Math.round(
                    recommendation.confidence * 100
                );

            return (
                `• ${recommendation.action}: ` +
                `${recommendation.reason} ` +
                `(${confidence}% confidence)`
            );
        });

    return lines.join("\n");
}


function formatDuplicates(duplicates) {
    if (!duplicates || !duplicates.length) {
        return "";
    }

    const groups = duplicates
        .slice(0, 5)
        .map((group) => {
            return (
                `• ${group.count} duplicate files: ` +
                group.files.join(", ")
            );
        });

    return groups.join("\n");
}


function formatScanResult(result) {
    const scanner = result.scanner || {};
    const summary = scanner.summary || {};
    const intelligence = result.intelligence || {};

    let response =
        `AI scan completed successfully.\n\n` +
        `Files found: ${scanner.files_found ?? 0}\n` +
        `Folders found: ${scanner.folders_found ?? 0}\n` +
        `Files analyzed: ${result.incremental?.files_analyzed ?? 0}\n` +
        `Files indexed: ${result.incremental?.files_indexed ?? 0}\n` +
        `Scan time: ${(summary.scan_time ?? 0).toFixed(2)} seconds`;

    const categories = intelligence.categories || {};
    const categoryEntries = Object.entries(categories);

    if (categoryEntries.length) {
        response += "\n\nCategories:\n";

        response += categoryEntries
            .map(([category, count]) => {
                return `• ${category}: ${count}`;
            })
            .join("\n");
    }

    const recommendations =
        formatRecommendations(
            result.recommendations
        );

    if (recommendations) {
        response +=
            "\n\nAI recommendations:\n" +
            recommendations;
    }

    const duplicates =
        formatDuplicates(result.duplicates);

    if (duplicates) {
        response +=
            "\n\nDuplicate groups:\n" +
            duplicates;
    }

    return response;
}


async function handleUserRequest(message) {
    const normalized = message
        .trim()
        .toLowerCase();

    if (!userFiles.length) {
        const loaded = await loadUserFiles();

        if (!loaded) {
            return;
        }
    }

    if (
        normalized.includes("largest") ||
        normalized.includes("biggest") ||
        normalized.includes("large")
    ) {
        const largest = getLargestFile();

        if (!largest) {
            addMessage(
                "I couldn't find any files in your account.",
                "assistant"
            );
            return;
        }

        addMessage(
            `Your largest file is "${largest.filename}" at ${formatBytes(largest.file_size || 0)}.`,
            "assistant"
        );

        return;
    }


    if (
        normalized.includes("pdf")
    ) {
        const pdfFiles = getPdfFiles();

        addMessage(
            pdfFiles.length
                ? `I found ${pdfFiles.length} PDF file(s):\n\n${formatFileList(pdfFiles)}`
                : "I couldn't find any PDF files.",
            "assistant"
        );

        return;
    }


    if (
        normalized.includes("recent") ||
        normalized.includes("latest")
    ) {
        const recentFiles = getRecentFiles();

        addMessage(
            recentFiles.length
                ? `Here are your recent files:\n\n${formatFileList(recentFiles)}`
                : "I couldn't find any files.",
            "assistant"
        );

        return;
    }


    if (
        normalized.includes("scan") ||
        normalized.includes("analyze") ||
        normalized.includes("organize") ||
        normalized.includes("duplicate")
    ) {
        const file = getLargestFile();

        if (!file) {
            addMessage(
                "There are no uploaded files available to scan.",
                "assistant"
            );
            return;
        }

        addMessage(
            `I'll run the real AI scan using "${file.filename}" as the directory entry point.`,
            "assistant"
        );

        showTyping();

        try {
            const result = await scanFile(file);

            removeTyping();

            addMessage(
                formatScanResult(result),
                "assistant"
            );

        } catch (error) {
            removeTyping();

            console.error("AI scan error:", error);

            addMessage(
                error.message ||
                "The AI scan could not be completed.",
                "assistant"
            );
        }

        return;
    }


    addMessage(
        `I can currently work with your real file index. You have ${userFiles.length} file(s) available. Try asking me to find your largest files, find PDFs, show recent files, or scan your files.`,
        "assistant"
    );
}


async function sendMessage(text) {
    const message = text.trim();

    if (!message || isLoading) {
        return;
    }

    isLoading = true;

    suggestions.hidden = true;
    chatInput.value = "";
    sendButton.disabled = true;

    addMessage(message, "user");
    showTyping();

    try {
        removeTyping();
        await handleUserRequest(message);

    } catch (error) {
        removeTyping();

        console.error("AI assistant error:", error);

        addMessage(
            error.message ||
            "Something went wrong while processing your request.",
            "assistant"
        );
    }

    isLoading = false;
    sendButton.disabled = false;
    chatInput.focus();
}


chatForm.addEventListener("submit", (event) => {
    event.preventDefault();

    sendMessage(chatInput.value);
});


suggestions
    .querySelectorAll(".suggestion")
    .forEach((suggestion) => {
        suggestion.addEventListener("click", () => {
            sendMessage(
                suggestion.dataset.message
            );
        });
    });


newChatButton.addEventListener("click", () => {
    messages.innerHTML = "";
    suggestions.hidden = false;
    chatInput.value = "";
    chatInput.focus();
});


backButton.addEventListener("click", () => {
    window.location.href =
        "../dashboard/index.html";
});


navItems.forEach((item) => {
    item.addEventListener("click", () => {
        const page = item.dataset.page;

        if (page === "dashboard") {
            window.location.href =
                "../dashboard/index.html";
            return;
        }

        if (page === "files") {
            window.location.href =
                "../search/index.html";
            return;
        }

        if (page === "settings") {
            window.location.href =
                "../settings/index.html";
        }
    });
});


document.addEventListener("DOMContentLoaded", async () => {
    const token = getAccessToken();

    if (!token) {
        addMessage(
            "Please sign in to use the AI Assistant.",
            "assistant"
        );
        return;
    }

    await loadUserFiles();
});
