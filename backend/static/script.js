// Replace your entire script.js with this clean working version

// ======================================================
// DASHBOARD INSIGHTS
// ======================================================
function getData() {
    const id = document.getElementById("studentId");
    const resultBox = document.getElementById("result");

    if (!id || !resultBox) return;

    const studentId = id.value.trim();

    if (!studentId) {
        resultBox.style.display = "block";
        resultBox.innerHTML = "⚠️ Please enter Student ID!";
        return;
    }

    resultBox.style.display = "block";
    resultBox.innerHTML = "⏳ Fetching AI Insights...";

    fetch("/insights/" + encodeURIComponent(studentId))
        .then(response => response.json())
        .then(data => {
            if (!data || data.error) {
                resultBox.innerHTML = "❌ " + (data.error || "No data found");
                return;
            }

            const mentor = data.mentor || {};
            const mentorName = mentor.mentor_name || "Not assigned";
            const expertise = mentor.expertise || "Not available";
            const sri = data.sri ? Number(data.sri).toFixed(2) : "0.00";

            resultBox.innerHTML = `
                <div style="text-align:left; line-height:1.6">
                    <b>🎓 Student ID:</b> ${data.student_id || "N/A"}<br>
                    <b>📊 Category:</b> ${data.category || "N/A"}<br>
                    <b>📈 SRI Score:</b> ${sri}<br><br>
                    <b>💡 Suggestion:</b><br>
                    ${data.suggestion || "No suggestion available"}<br><br>
                    <b>👨‍🏫 Mentor:</b> ${mentorName}<br>
                    <b>🧠 Expertise:</b> ${expertise}
                </div>
            `;
        })
        .catch(error => {
            console.error(error);
            resultBox.innerHTML = "⚠️ Server error. Try again later.";
        });
}


// ======================================================
// HELPER
// ======================================================
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


// ======================================================
// CHATBOT
// ======================================================
function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    if (!input || !chatBox) return;

    const message = input.value.trim();
    if (!message) return;

    // Show user message
    chatBox.innerHTML += `
        <div class="user-box">
            <h3>You</h3>
            <p>${escapeHtml(message)}</p>
        </div>
    `;

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Loading
    chatBox.innerHTML += `
        <div class="bot-box" id="loading-message">
            <h3>AI Mentor</h3>
            <p>⏳ Thinking...</p>
        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        const loading = document.getElementById("loading-message");
        if (loading) loading.remove();

        const responseText = data.response || "No response.";
        const safeResponse = escapeHtml(responseText);

        // Create unique ID for this response
        const speechId =
            "speech_" + Date.now() + "_" + Math.floor(Math.random() * 10000);

        // Store response text globally
        window[speechId] = responseText;

        // Add AI response
        chatBox.innerHTML += `
            <div class="bot-box">
                <h3 style="display:flex; justify-content:space-between; align-items:center;">
                    <span>AI Mentor</span>
                    <button
                        type="button"
                        onclick="speakText(window['${speechId}'])"
                        style="
                            padding:6px 12px;
                            font-size:14px;
                            border:none;
                            border-radius:8px;
                            cursor:pointer;
                            background:#2563eb;
                            color:white;
                        ">
                        🔊 Listen
                    </button>
                </h3>
                <p>${safeResponse}</p>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error(error);

        const loading = document.getElementById("loading-message");
        if (loading) loading.remove();

        chatBox.innerHTML += `
            <div class="bot-box">
                <h3>AI Mentor</h3>
                <p>⚠️ Error connecting to AI service.</p>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;
    });
}


// ======================================================
// ENTER KEY
// ======================================================
function handleKeyPress(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        sendMessage();
    }
}


// ======================================================
// CATEGORY
// ======================================================
function setCategory(category) {
    fetch("/set_preferences", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            category: category
        })
    })
    .then(response => response.json())
    .then(data => {
        const currentCategory = document.getElementById("current-category");
        if (currentCategory) {
            currentCategory.textContent = data.category;
        }
    })
    .catch(error => {
        console.error(error);
    });
}


// ======================================================
// VOICE INPUT
// ======================================================
let recognition = null;
let isListening = false;

function startVoice() {
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("Speech recognition is not supported.");
        return;
    }

    recognition = new SpeechRecognition();

    const languageSelect = document.getElementById("language-select");
    recognition.lang = languageSelect ? languageSelect.value : "en-US";

    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    isListening = true;

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById("user-input");

        if (input) {
            input.value = transcript;
            input.focus();
        }
    };

    recognition.onerror = function(event) {
        console.error("Speech error:", event.error);
        isListening = false;
    };

    recognition.onend = function() {
        isListening = false;
    };

    recognition.start();
}


// ======================================================
// STOP VOICE
// ======================================================
function stopVoice() {
    if (recognition && isListening) {
        recognition.stop();
        isListening = false;
    }

    if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
    }
}


// ======================================================
// TEXT TO SPEECH
// ======================================================
function speakText(text) {
    if (!window.speechSynthesis) {
        alert("Text-to-speech is not supported.");
        return;
    }

    if (!text || text.trim() === "") {
        return;
    }

    // Stop current speech
    window.speechSynthesis.cancel();

    // Wait a moment before starting new speech
    setTimeout(() => {
        const utterance = new SpeechSynthesisUtterance(text);

        const languageSelect = document.getElementById("language-select");
        utterance.lang = languageSelect
            ? languageSelect.value
            : "en-US";

        utterance.rate = 1;
        utterance.pitch = 1;
        utterance.volume = 1;

        // Optional debugging
        utterance.onstart = () => console.log("Speech started");
        utterance.onend = () => console.log("Speech ended");
        utterance.onerror = (e) => console.error("Speech error:", e);

        window.speechSynthesis.speak(utterance);
    }, 250); // Important delay
}
function bookSession(mentorId) {

    fetch("/book_session", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            mentor_id: mentorId
        })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    });

}