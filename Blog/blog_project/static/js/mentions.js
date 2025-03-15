document.addEventListener('DOMContentLoaded', function() {
    const mentionableTextareas = document.querySelectorAll('textarea[data-mention="true"]');
    
    // List of users for autocomplete (will populate via AJAX)
    let users = [];

    // Fetch users for autocomplete
    fetch('/api/users/')
        .then(response => response.json())
        .then(data => {
            users = data;
        })
        .catch(error => console.error('Error loading users:', error));

    mentionableTextareas.forEach(textarea => {
        let mentionDropdown = document.createElement('div');
        mentionDropdown.className = 'mention-dropdown';
        mentionDropdown.style.display = 'none';
        mentionDropdown.style.position = 'absolute';
        mentionDropdown.style.border = '1px solid #ccc';
        mentionDropdown.style.background = 'white';
        mentionDropdown.style.maxHeight = '200px';
        mentionDropdown.style.overflowY = 'auto';
        mentionDropdown.style.zIndex = '1000';
        textarea.parentNode.style.position = 'relative';
        textarea.parentNode.appendChild(mentionDropdown);

        // Track if we're in the process of a mention
        let mentioning = false;
        let mentionStart = 0;
        let mentionText = '';

        textarea.addEventListener('input', function() {
            const text = textarea.value;
            const cursorPos = textarea.selectionStart;
            
            // Check if we're in the middle of typing a mention
            if (text.charAt(cursorPos - 1) === '@' && (cursorPos === 1 || /\s/.test(text.charAt(cursorPos - 2)))) {
                mentioning = true;
                mentionStart = cursorPos - 1;
                mentionText = '';
                showMentionDropdown('');
            } else if (mentioning) {
                // If we pressed space or we're no longer at a position after the @ symbol, stop mentioning
                if (cursorPos <= mentionStart || /\s/.test(text.charAt(cursorPos - 1))) {
                    mentioning = false;
                    mentionDropdown.style.display = 'none';
                } else {
                    // Update the mention text
                    mentionText = text.substring(mentionStart + 1, cursorPos);
                    showMentionDropdown(mentionText);
                }
            }
        });

        function showMentionDropdown(query) {
            // Filter users based on query
            const filtered = users.filter(user => 
                user.username.toLowerCase().includes(query.toLowerCase())
            );
            
            // Build dropdown content
            mentionDropdown.innerHTML = '';
            if (filtered.length > 0) {
                filtered.forEach(user => {
                    const item = document.createElement('div');
                    item.className = 'mention-item';
                    item.style.padding = '5px 10px';
                    item.style.cursor = 'pointer';
                    item.textContent = user.username;
                    
                    item.addEventListener('mouseenter', function() {
                        this.style.backgroundColor = '#f0f0f0';
                    });
                    
                    item.addEventListener('mouseleave', function() {
                        this.style.backgroundColor = 'transparent';
                    });
                    
                    item.addEventListener('click', function() {
                        completeMention(user.username);
                    });
                    
                    mentionDropdown.appendChild(item);
                });
                
                // Position and show the dropdown
                const textAreaRect = textarea.getBoundingClientRect();
                mentionDropdown.style.display = 'block';
                
                // Find the position of the caret
                const dummy = document.createElement('div');
                dummy.style.position = 'absolute';
                dummy.style.top = '0';
                dummy.style.left = '0';
                dummy.style.visibility = 'hidden';
                dummy.style.whiteSpace = 'pre-wrap';
                dummy.style.font = window.getComputedStyle(textarea).font;
                dummy.textContent = textarea.value.substring(0, mentionStart);
                document.body.appendChild(dummy);
                
                const caretPos = dummy.getBoundingClientRect();
                document.body.removeChild(dummy);
                
                // Position dropdown below the @ symbol
                mentionDropdown.style.top = (caretPos.height + 5) + 'px';
                mentionDropdown.style.left = '0';
            } else {
                mentionDropdown.style.display = 'none';
            }
        }

        function completeMention(username) {
            const text = textarea.value;
            const newText = text.substring(0, mentionStart) + '@' + username + ' ' + text.substring(textarea.selectionStart);
            textarea.value = newText;
            mentioning = false;
            mentionDropdown.style.display = 'none';
            
            // Move cursor after the inserted username
            const newCursorPos = mentionStart + username.length + 2; // +2 for @ and space
            textarea.setSelectionRange(newCursorPos, newCursorPos);
            textarea.focus();
        }

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!textarea.contains(e.target) && !mentionDropdown.contains(e.target)) {
                mentionDropdown.style.display = 'none';
                mentioning = false;
            }
        });
    });
});