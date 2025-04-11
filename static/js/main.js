document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const queryForm = document.getElementById('query-form');
    const queryInput = document.getElementById('query-input');
    const chatContainer = document.getElementById('chat-container');
    const themeToggle = document.getElementById('theme-toggle');
    
    // Theme Toggle
    themeToggle.addEventListener('click', function() {
        const htmlElement = document.documentElement;
        const currentTheme = htmlElement.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        htmlElement.setAttribute('data-bs-theme', newTheme);
        
        // Update toggle button text and icon
        if (newTheme === 'dark') {
            this.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
        } else {
            this.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
        }
    });
    
    // Query Form Submission
    queryForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const query = queryInput.value.trim();
        if (!query) return;
        
        // Add user message to chat
        addUserMessage(query);
        
        // Clear input
        queryInput.value = '';
        
        // Show loading indicator
        addLoadingIndicator();
        
        // Send query to backend
        fetch('/api/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading indicator
            removeLoadingIndicator();
            
            if (data.success) {
                // Add system response
                addSystemResponse(data);
            } else {
                // Add error message
                addErrorMessage(data.error || 'An error occurred while processing your query.');
            }
        })
        .catch(error => {
            // Remove loading indicator
            removeLoadingIndicator();
            
            // Add error message
            addErrorMessage('Failed to connect to the server. Please try again later.');
            console.error('Error:', error);
        });
    });
    
    // Add user message to chat
    function addUserMessage(message) {
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container user-message-container';
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.textContent = message;
        
        messageContainer.appendChild(messageElement);
        chatContainer.appendChild(messageContainer);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    // Add system response to chat
    function addSystemResponse(data) {
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container system-message-container';
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message system-message';
        
        // Add response message
        const responseParagraph = document.createElement('p');
        responseParagraph.textContent = getResponseMessage(data.query);
        messageElement.appendChild(responseParagraph);
        
        // Add recommendations
        if (data.recommendations && data.recommendations.length > 0) {
            const recommendationContainer = document.createElement('div');
            recommendationContainer.className = 'recommendation-container';
            
            data.recommendations.forEach((rec, index) => {
                const card = createRecommendationCard(rec, index);
                recommendationContainer.appendChild(card);
            });
            
            messageElement.appendChild(recommendationContainer);
        } else {
            const noResultsParagraph = document.createElement('p');
            noResultsParagraph.textContent = "I couldn't find any matching assessments. Please try a different query.";
            messageElement.appendChild(noResultsParagraph);
        }
        
        messageContainer.appendChild(messageElement);
        chatContainer.appendChild(messageContainer);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    // Create recommendation card
    function createRecommendationCard(recommendation, index) {
        const card = document.createElement('div');
        card.className = 'recommendation-card card';
        card.style.animationDelay = `${0.1 * (index + 1)}s`;
        
        // Card content
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        // Similarity score
        const score = document.createElement('div');
        score.className = 'recommendation-score';
        score.textContent = `Match: ${Math.round(recommendation.similarity * 100)}%`;
        cardBody.appendChild(score);
        
        // Title with link
        const title = document.createElement('h5');
        title.className = 'card-title';
        
        const link = document.createElement('a');
        link.href = recommendation.url;
        link.target = '_blank';
        link.textContent = recommendation.title;
        
        title.appendChild(link);
        cardBody.appendChild(title);
        
        // Description
        const description = document.createElement('p');
        description.className = 'card-text';
        description.textContent = recommendation.description;
        cardBody.appendChild(description);
        
        card.appendChild(cardBody);
        return card;
    }
    
    // Add loading indicator to chat
    function addLoadingIndicator() {
        const loadingContainer = document.createElement('div');
        loadingContainer.className = 'message-container system-message-container';
        loadingContainer.id = 'loading-indicator';
        
        const loadingElement = document.createElement('div');
        loadingElement.className = 'loading-indicator system-message';
        
        const loadingDots = document.createElement('div');
        loadingDots.className = 'loading-dots';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            loadingDots.appendChild(dot);
        }
        
        loadingElement.appendChild(loadingDots);
        loadingContainer.appendChild(loadingElement);
        chatContainer.appendChild(loadingContainer);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    // Remove loading indicator from chat
    function removeLoadingIndicator() {
        const loadingIndicator = document.getElementById('loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }
    }
    
    // Add error message to chat
    function addErrorMessage(message) {
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container system-message-container';
        
        const messageElement = document.createElement('div');
        messageElement.className = 'message system-message';
        
        const errorIcon = document.createElement('i');
        errorIcon.className = 'fas fa-exclamation-triangle me-2';
        
        const errorText = document.createElement('span');
        errorText.textContent = message;
        
        messageElement.appendChild(errorIcon);
        messageElement.appendChild(errorText);
        messageContainer.appendChild(messageElement);
        chatContainer.appendChild(messageContainer);
        
        // Scroll to bottom
        scrollToBottom();
    }
    
    // Generate response message based on query
    function getResponseMessage(query) {
        const responses = [
            `Here are some SHL assessments that might be relevant for "${query}":`,
            `Based on your interest in "${query}", I found these assessments:`,
            `For "${query}", I recommend the following SHL assessments:`,
            `I've found these relevant SHL assessments matching "${query}":`
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }
    
    // Scroll chat to bottom
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Focus input on page load
    queryInput.focus();
});
