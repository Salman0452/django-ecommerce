(function () {
    const siteHeader = document.querySelector('.site-header');
    const menuToggle = document.querySelector('.js-menu-toggle');
    const chatWidget = document.querySelector('.js-chat-widget');
    const chatToggle = document.querySelector('.js-chat-toggle');
    const chatClose = document.querySelector('.js-chat-close');
    const chatForm = document.querySelector('.js-chat-form');
    const chatInput = document.querySelector('.js-chat-input');
    const chatMessages = document.querySelector('.js-chat-messages');
    const flashMessages = Array.from(document.querySelectorAll('.js-flash-message'));
    const cartCountElement = document.querySelector('[data-cart-count]');
    const csrfToken = getCsrfToken();

    function getCsrfToken() {
        const metaToken = document.querySelector('meta[name="csrf-token"]');

        if (metaToken && metaToken.content) {
            return metaToken.content;
        }

        const cookieMatch = document.cookie.split('; ').find((cookie) => cookie.startsWith('csrftoken='));
        return cookieMatch ? decodeURIComponent(cookieMatch.split('=')[1]) : '';
    }

    function setMenuState(isOpen) {
        if (!siteHeader || !menuToggle) {
            return;
        }

        siteHeader.classList.toggle('is-open', isOpen);
        menuToggle.setAttribute('aria-expanded', String(isOpen));
    }

    function setChatState(isOpen) {
        if (!chatWidget || !chatToggle || !chatClose) {
            return;
        }

        chatWidget.classList.toggle('is-open', isOpen);
        chatToggle.setAttribute('aria-expanded', String(isOpen));

        const panel = chatWidget.querySelector('#chat-panel');
        if (panel) {
            panel.setAttribute('aria-hidden', String(!isOpen));
        }

        if (isOpen && chatInput) {
            chatInput.focus();
        }
    }

    function openChatWidget() {
        setChatState(true);
        if (chatWidget) {
            chatWidget.scrollIntoView({ behavior: 'smooth' });
        }
    }

    window.openChatWidget = openChatWidget;

    function createChatBubble(messageText, messageType) {
        const messageBubble = document.createElement('div');
        messageBubble.className = `chat-message chat-message--${messageType}`;

        const paragraph = document.createElement('p');
        paragraph.textContent = messageText;
        messageBubble.appendChild(paragraph);
        return messageBubble;
    }

    function appendChatMessage(messageText, messageType) {
        if (!chatMessages) {
            return;
        }

        chatMessages.appendChild(createChatBubble(messageText, messageType));
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function updateCartItemCount(count) {
        if (!cartCountElement) {
            return;
        }

        cartCountElement.textContent = String(count);
    }

    function dismissFlashMessage(messageElement) {
        if (!messageElement) {
            return;
        }

        messageElement.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(-4px)';

        window.setTimeout(() => {
            messageElement.remove();
        }, 200);
    }

    window.updateCartItemCount = updateCartItemCount;

    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            const isOpen = !siteHeader.classList.contains('is-open');
            setMenuState(isOpen);
        });
    }

    if (chatToggle) {
        chatToggle.addEventListener('click', () => {
            const isOpen = !chatWidget.classList.contains('is-open');
            setChatState(isOpen);
        });
    }

    if (chatClose) {
        chatClose.addEventListener('click', () => setChatState(false));
    }

    document.querySelectorAll('[data-open-chat]').forEach((trigger) => {
        trigger.addEventListener('click', () => openChatWidget());
    });

    if (chatForm) {
        chatForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const messageValue = chatInput ? chatInput.value.trim() : '';
            if (!messageValue) {
                return;
            }

            appendChatMessage(messageValue, 'user');

            if (chatInput) {
                chatInput.value = '';
            }

            const typingBubble = createChatBubble('Thinking...', 'assistant');
            typingBubble.dataset.typing = 'true';

            if (chatMessages) {
                chatMessages.appendChild(typingBubble);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            try {
                const response = await fetch('/api/v1/chatbot/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ message: messageValue }),
                });

                const responseData = await response.json();

                if (typingBubble.isConnected) {
                    typingBubble.remove();
                }

                if (!response.ok) {
                    const errorMessage = responseData.detail || 'Unable to send message.';
                    appendChatMessage(errorMessage, 'assistant');
                    return;
                }

                appendChatMessage(responseData.response || 'I did not receive a response.', 'assistant');
            } catch (error) {
                if (typingBubble.isConnected) {
                    typingBubble.remove();
                }

                appendChatMessage('Something went wrong. Please try again.', 'assistant');
            }
        });
    }

    flashMessages.forEach((messageElement) => {
        window.setTimeout(() => dismissFlashMessage(messageElement), 4000);

        const dismissButton = messageElement.querySelector('.js-flash-close');
        if (dismissButton) {
            dismissButton.addEventListener('click', () => dismissFlashMessage(messageElement));
        }
    });

    document.addEventListener('click', (event) => {
    if (siteHeader && siteHeader.classList.contains('is-open') && !event.target.closest('.site-header')) {
        setMenuState(false);
    }

    if (chatWidget && chatWidget.classList.contains('is-open') 
        && !event.target.closest('.js-chat-widget')
        && !event.target.closest('[data-open-chat]')) {
        setChatState(false);
    }
});
})();