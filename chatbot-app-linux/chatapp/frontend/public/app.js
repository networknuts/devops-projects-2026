const chatForm = document.getElementById('chat-form');
const questionInput = document.getElementById('question');
const chatWindow = document.getElementById('chat-window');
const newChatButton = document.getElementById('new-chat');

let conversationId = null;
const apiBaseUrl = window.APP_CONFIG.API_BASE_URL;

function appendMessage(role, text) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.innerHTML = `
    <div class="message-role">${role === 'user' ? 'You' : 'Assistant'}</div>
    <div class="message-text"></div>
  `;
  div.querySelector('.message-text').textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendQuestion(question) {
  const response = await fetch(`${apiBaseUrl}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      question,
      conversation_id: conversationId
    })
  });

  if (!response.ok) {
    let detail = 'Request failed';
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }

  return response.json();
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = questionInput.value.trim();
  if (!question) return;

  appendMessage('user', question);
  questionInput.value = '';
  questionInput.disabled = true;

  try {
    appendMessage('assistant', 'Thinking...');
    const thinkingNode = chatWindow.lastChild;

    const data = await sendQuestion(question);
    conversationId = data.conversation_id;
    thinkingNode.querySelector('.message-text').textContent = data.answer;
  } catch (error) {
    appendMessage('assistant', `Error: ${error.message}`);
  } finally {
    questionInput.disabled = false;
    questionInput.focus();
  }
});

newChatButton.addEventListener('click', () => {
  conversationId = null;
  chatWindow.innerHTML = '';
  questionInput.value = '';
  questionInput.focus();
});
