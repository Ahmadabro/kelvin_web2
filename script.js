let activeBase64Image = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

// UI Setup Hooks
document.getElementById('sendBtn').addEventListener('click', sendMessage);
document.getElementById('userInput').addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });
document.getElementById('uploadBtn').addEventListener('click', () => document.getElementById('imageInput').click());
document.getElementById('imageInput').addEventListener('change', handleImageSelection);
document.getElementById('removeImgBtn').addEventListener('click', removeAttachedImage);
document.getElementById('micBtn').addEventListener('click', toggleAudioRecording);

// Handle Local File System Selection
function handleImageSelection(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
        activeBase64Image = event.target.result;
        document.getElementById('imagePreview').src = activeBase64Image;
        document.getElementById('imagePreviewContainer').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function removeAttachedImage() {
    activeBase64Image = null;
    document.getElementById('imageInput').value = '';
    document.getElementById('imagePreviewContainer').classList.add('hidden');
}

// Media Recording Pipeline
async function toggleAudioRecording() {
    const micBtn = document.getElementById('micBtn');
    
    if (!isRecording) {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Audio capturing is not supported on your current web environment browser.");
            return;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                // Convert audio to base64 string to safely forward via json standard request
                const reader = new FileReader();
                reader.onloadend = async () => {
                    const base64Audio = reader.result.split(',')[1];
                    await sendAudioToServer(base64Audio);
                };
                reader.readAsDataURL(audioBlob);
                stream.getTracks().forEach(track => track.stop()); // Release mic hardware
            };

            mediaRecorder.start();
            isRecording = true;
            micBtn.classList.add('recording-active');
        } catch (err) {
            console.error("Microphone capture access denied:", err);
        }
    } else {
        mediaRecorder.stop();
        isRecording = false;
        micBtn.classList.remove('recording-active');
    }
}

async function sendAudioToServer(base64Audio) {
    const chatBox = document.getElementById('chatBox');
    const loadingMessage = appendMessage("Transcribing audio...", 'ai-message', false);
    
    try {
        // FIXED: Changed endpoint route path from '/api/chat' to unified '/api'
        const response = await fetch('/api', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ audioData: base64Audio })
        });
        const data = await response.json();
        loadingMessage.remove();

        if (response.ok) {
            // Put transcribed speech text straight into the prompt field for clarity
            // If using the placeholder mock string, it appends the message instead
            if (data.reply) {
                const aiDiv = document.createElement('div');
                aiDiv.className = 'message ai-message';
                aiDiv.innerHTML = data.reply;
                chatBox.appendChild(aiDiv);
            } else {
                document.getElementById('userInput').value = data.transcription || "";
            }
        } else {
            appendMessage(`⚠️ Audio Transcription Error: ${data.error}`, 'ai-message', false);
        }
    } catch (e) {
        loadingMessage.remove();
        console.error(e);
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const inputEl = document.getElementById('userInput');
    const chatBox = document.getElementById('chatBox');
    const messageText = inputEl.value.trim();

    if (!messageText && !activeBase64Image) return;

    // Build user view interface component
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message user-message';
    if (activeBase64Image) {
        const img = document.createElement('img');
        img.src = activeBase64Image;
        img.className = 'chat-msg-img';
        msgDiv.appendChild(img);
    }
    if (messageText) {
        const textNode = document.createTextNode(messageText);
        msgDiv.appendChild(textNode);
    }
    chatBox.appendChild(msgDiv);
    
    // Save image instance to send, then clear input bar UI components immediately
    const imageToSend = activeBase64Image;
    inputEl.value = '';
    removeAttachedImage();
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = '<span></span><span></span><span></span>';
    chatBox.appendChild(indicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch('/api', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText, imageData: imageToSend })
        });

        const data = await response.json();
        indicator.remove();

        if (response.ok) {
            const aiDiv = document.createElement('div');
            aiDiv.className = 'message ai-message';
            aiDiv.innerHTML = marked.parse(data.reply);
            chatBox.appendChild(aiDiv);
        } else {
            appendMessage(`⚠️ Error: ${data.error}`, 'ai-message', false);
        }
    } catch (error) {
        indicator.remove();
        console.error(error);
    }
    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendMessage(text, className, useMarkdown) {
    const chatBox = document.getElementById('chatBox');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${className}`;
    msgDiv.textContent = text;
    chatBox.appendChild(msgDiv);
    return msgDiv;
}