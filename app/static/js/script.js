var socket = io();

// Função para adicionar uma mensagem ao chat
function addMessage(message, isUser) {
    var messageDiv = document.createElement('div');
    messageDiv.className = isUser ? 'message user' : 'message server';
    messageDiv.innerHTML = `<strong>${isUser ? 'Você' : message.username}:</strong> ${message.content}`;
    document.getElementById('messages').appendChild(messageDiv);
    scrollToLastMessage();
}

// Função para enviar uma notificação
function sendNotification(message) {
    if (Notification.permission === 'granted') {
        new Notification('Nova mensagem', {
            body: 'Uma pedra enviada por ' + message.username + ' quebrou sua janela',
            icon: '/static/icons/icon-192x192.png' // Opcional: caminho para um ícone
        });
    }
}

// Função para rolar para a última mensagem
function scrollToLastMessage() {
    var messagesDiv = document.getElementById('messages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Solicita permissão para enviar notificações
function requestNotificationPermission() {
    if (Notification.permission !== 'granted') {
        Notification.requestPermission();
    }
}

// Função para alternar o modo escuro
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    document.querySelector('.chat-container').classList.toggle('dark-mode');
    document.querySelector('.chat-header').classList.toggle('dark-mode');
    document.querySelector('.chat-input').classList.toggle('dark-mode');
    document.getElementById('myMessage').classList.toggle('dark-mode');
    document.getElementById('sendBtn').classList.toggle('dark-mode');
    document.querySelectorAll('.message').forEach(function(message) {
        message.classList.toggle('dark-mode');
    });
}

// Inicializa os eventos do Socket.IO
function initializeSocketEvents() {
    socket.on('message', function(data) {
        addMessage(data, false); // Mensagem recebida (não é do usuário atual)
        sendNotification(data); // Envia uma notificação
    });
}

// Inicializa os eventos da interface do usuário
function initializeUIEvents() {
    document.getElementById('sendBtn').onclick = function() {
        var message = document.getElementById('myMessage').value;
        if (message) {
            // Exibe a mensagem localmente como "enviada"
            addMessage({ username: 'Você', content: message }, true);

            // Envia a mensagem para o servidor via Socket.IO
            socket.send(message);
            document.getElementById('myMessage').value = '';
        }
    };

    document.getElementById('myMessage').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('sendBtn').click();
        }
    });

    document.getElementById('menuButton').onclick = function() {
        var dropdown = document.getElementById('menuDropdown');
        dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
    };

    window.onclick = function(event) {
        if (!event.target.matches('#menuButton')) {
            var dropdown = document.getElementById('menuDropdown');
            if (dropdown.style.display === 'block') {
                dropdown.style.display = 'none';
            }
        }
    };

    document.getElementById('darkModeToggle').onclick = toggleDarkMode;
}

// Função de inicialização
function initialize() {
    requestNotificationPermission();
    initializeSocketEvents();
    initializeUIEvents();
    scrollToLastMessage();

    if ('serviceWorker' in navigator && 'PushManager' in window) {
        navigator.serviceWorker.register('/static/js/service-worker.js')
        .then(function(swReg) {
            console.log('Service Worker is registered', swReg);

            swReg.pushManager.getSubscription()
            .then(function(subscription) {
                if (subscription === null) {
                    // Solicitar permissão para notificações
                    Notification.requestPermission().then(function(permission) {
                        if (permission === 'granted') {
                            subscribeUser(swReg);
                        }
                    });
                }
            });
        })
        .catch(function(error) {
            console.error('Service Worker Error', error);
        });
    }
}

function subscribeUser(swReg) {
    const applicationServerKey = urlB64ToUint8Array('BKGeyfjwHzKcgPEM0I-XqudWHWiSVuOIFcBs5dLv5hOy9BhAaFbznVbsHqqi8zXzHcHefAMa0qpIuDVI4vAMKvI');
    swReg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey
    })
    .then(function(subscription) {
        console.log('User is subscribed:', subscription);
        // Enviar a assinatura para o servidor
        fetch('/subscribe', {
            method: 'POST',
            body: JSON.stringify(subscription),
            headers: {
                'Content-Type': 'application/json'
            }
        });
    })
    .catch(function(err) {
        console.log('Failed to subscribe the user: ', err);
    });
}

function urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Inicializa a aplicação ao carregar a página
window.onload = function() {
    initialize();
};