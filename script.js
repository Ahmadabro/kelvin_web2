document.getElementById('sendBtn').addEventListener('click', sendMessage);
document.getElementById('userInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage() {
    const inputEl = document.getElementById('userInput');
    const chatBox = document.getElementById('chatBox');
    const messageText = inputEl.value.trim();

    if (!messageText) return;

    // 1. Render User Message Safely
    appendMessage(messageText, 'user-message', false);
    inputEl.value = '';

    // 2. Display Dynamic Loading Wave Indicator
    const typingIndicator = createTypingIndicator();
    chatBox.appendChild(typingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        // 3. Post to Vercel Serverless Endpoint
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText })
        });

        const data = await response.json();
        typingIndicator.remove(); // Drop loading indicator

        if (response.ok) {
            // Render via Markdown Parser library for code blocks/bold structures
            appendMessage(data.reply, 'ai-message', true);
        } else {
            appendMessage(`⚠️ Server Error: ${data.error || 'Failed to capture data.'}`, 'ai-message', false);
        }

    } catch (error) {
        typingIndicator.remove();
        appendMessage('⚠️ Connection error. Please verify your Vercel configurations.', 'ai-message', false);
        console.error(error);
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendMessage(text, className, useMarkdown) {
    const chatBox = document.getElementById('chatBox');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${className}`;
    
    if (useMarkdown && typeof marked !== 'undefined') {
        msgDiv.innerHTML = marked.parse(text);
    } else {
        msgDiv.textContent = text;
    }
    
    chatBox.appendChild(msgDiv);
    return msgDiv;
}

function createTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    return indicator;
}