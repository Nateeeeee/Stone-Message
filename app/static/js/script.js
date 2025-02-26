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
            icon: '/path/to/icon.png' // Opcional: caminho para um ícone
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
}

// Inicializa a aplicação ao carregar a página
window.onload = initialize;