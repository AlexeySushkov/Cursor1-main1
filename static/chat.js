const chatArea = document.getElementById('chat-area');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const streamingToggle = document.getElementById('streaming-toggle');
const clearHistoryToggle = document.getElementById('clear-history-toggle');

let dialogContext = [];

function removeInlineStyles(element) {
    if (element.removeAttribute) element.removeAttribute('style');
    for (let i = 0; i < element.children.length; i++) {
        removeInlineStyles(element.children[i]);
    }
}

function appendMessage(role, text, isHTML = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'msg ' + role;
    
    if (isHTML) {
        msgDiv.innerHTML = text;
        removeInlineStyles(msgDiv);
        console.log('Setting innerHTML:', text);
        console.log('Resulting HTML structure:', msgDiv.outerHTML);
    } else {
        msgDiv.textContent = text;
        console.log('Setting textContent:', text);
    }
    
    chatArea.appendChild(msgDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
    return msgDiv;
}

function updateMessage(msgDiv, text, isHTML = false) {
    if (isHTML) {
        msgDiv.innerHTML = text;
        removeInlineStyles(msgDiv);
    } else {
        msgDiv.textContent = text;
    }
    chatArea.scrollTop = chatArea.scrollHeight;
}

function limitContext(context, maxMessages = 10) {
    // Keep only the last maxMessages messages to prevent context overflow
    if (context.length > maxMessages) {
        return context.slice(-maxMessages);
    }
    return context;
}

function clearChatHistory() {
    // Clear the chat area
    chatArea.innerHTML = '';
    // Clear the dialog context
    dialogContext = [];
    // Uncheck the clear history toggle
    clearHistoryToggle.checked = false;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userMsg = messageInput.value.trim();
    if (!userMsg) return;
    
    // Check if we need to clear history
    const shouldClearHistory = clearHistoryToggle.checked;
    if (shouldClearHistory) {
        clearChatHistory();
    }
    
    appendMessage('user', userMsg);
    dialogContext.push({ role: 'user', content: userMsg });
    messageInput.value = '';
    
    // Limit context to prevent API errors
    const limitedContext = limitContext(dialogContext);
    
    const isStreaming = streamingToggle.checked;
    console.log('Streaming mode:', isStreaming);
    
    if (isStreaming) {
        console.log('Using STREAMING mode');
        // Streaming response - collect raw markdown first
        const aiMsgDiv = appendMessage('ai', '');
        let fullResponse = '';
        
        try {
            const formData = new URLSearchParams({
                message: userMsg,
                context: JSON.stringify(limitedContext),
                streaming: 'true'
            });
            
            console.log('Sending streaming request with data:', formData.toString());
            
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData,
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            
            if (!response.ok) throw new Error('Network response was not ok');
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                fullResponse += chunk;
                
                // Convert markdown to HTML in real-time
                try {
                    const htmlContent = marked.parse(fullResponse);
                    updateMessage(aiMsgDiv, htmlContent, true); // Use HTML formatting
                    removeInlineStyles(aiMsgDiv); // Remove inline styles after every update
                    
                    // Apply inline styles for streaming too
                    const h3Elements = aiMsgDiv.querySelectorAll('h3');
                    h3Elements.forEach(h3 => {
                        h3.style.color = 'red';
                        h3.style.fontSize = '24px';
                        h3.style.background = 'yellow';
                        h3.style.margin = '8px 0 4px 0';
                        h3.style.fontWeight = '600';
                    });
                    
                    const strongElements = aiMsgDiv.querySelectorAll('strong');
                    strongElements.forEach(strong => {
                        strong.style.color = 'blue';
                        strong.style.fontWeight = '600';
                    });
                    
                    const pElements = aiMsgDiv.querySelectorAll('p');
                    pElements.forEach(p => {
                        p.style.background = 'lightgray';
                        p.style.padding = '10px';
                        p.style.margin = '6px 0';
                    });
                } catch (parseError) {
                    console.log('Markdown parse error, using raw text:', parseError);
                    updateMessage(aiMsgDiv, fullResponse, false);
                }
            }
            
        } catch (err) {
            console.error('Streaming error:', err);
            updateMessage(aiMsgDiv, 'Error: Could not get streaming response.');
        }
        
        dialogContext.push({ role: 'ai', content: fullResponse });
        
    } else {
        console.log('Using REGULAR mode');
        // Regular response - get formatted HTML
        appendMessage('ai', '...');
        try {
            const resp = await fetch('/chat', {
                method: 'POST',
                body: new URLSearchParams({
                    message: userMsg,
                    context: JSON.stringify(limitedContext),
                    streaming: 'false'
                }),
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            const data = await resp.json();
            console.log('Received response:', data.answer);
            console.log('Response type:', typeof data.answer);
            console.log('Contains HTML tags:', data.answer.includes('<'));
            // Remove the '...' placeholder
            chatArea.removeChild(chatArea.lastChild);
            const aiMsgDiv = appendMessage('ai', data.answer, true); // Use HTML formatting
            console.log('AI message div HTML:', aiMsgDiv.innerHTML);
            console.log('AI message div text:', aiMsgDiv.textContent);
            dialogContext.push({ role: 'ai', content: data.answer });
        } catch (err) {
            console.error('Regular response error:', err);
            chatArea.removeChild(chatArea.lastChild);
            appendMessage('ai', 'Error: Could not get response.');
        }
    }
}); 