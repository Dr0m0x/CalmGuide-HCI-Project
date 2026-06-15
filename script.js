const chatWindow = document.getElementById("chat-window");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const resetBtn = document.getElementById("reset-btn");

const stressCountEl = document.getElementById("stress-count");
const eduCountEl = document.getElementById("edu-count");
const positiveCountEl = document.getElementById("positive-count");

function appendMessage(text, sender) {
    const msg = document.createElement("div");
    msg.classList.add("message", sender);
    msg.textContent = text;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function updateStats(stats) {
    stressCountEl.textContent = stats.stress_count;
    eduCountEl.textContent = stats.edu_count;
    positiveCountEl.textContent = stats.positive_count;
}

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    appendMessage(message, "user");
    userInput.value = "";

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });
        const data = await res.json();

        if (data.response) {
            appendMessage(data.response, "bot");
            updateStats(data.stats);
        } else {
            appendMessage("Sorry, something went wrong.", "bot");
        }
    } catch (err) {
        appendMessage("Error connecting to the server.", "bot");
    }
});

resetBtn.addEventListener("click", async () => {
    await fetch("/reset", { method: "POST" });
    chatWindow.innerHTML = "";
    appendMessage(
        "Session reset. Hi, I'm CalmGuide. Tell me how you're feeling, or ask me a question about stress, anxiety, or mindfulness.",
        "bot"
    );
    updateStats({ stress_count: 0, edu_count: 0, positive_count: 0 });
});
