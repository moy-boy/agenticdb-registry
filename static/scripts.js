function setPlaceholderText() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        if (textarea.value.trim() === '') {
            textarea.value = textarea.placeholder;
        }
    });
}

async function submitAdd() {
    let content = document.getElementById('add-textbox').value;
    document.getElementById('add-response').value = ''; // Clear response area
    if (!content) {
        content = document.getElementById('add-textbox').placeholder;
    }
    try {
        const response = await fetch('/agents', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-yaml',
            },
            body: content,
        });
        const responseText = await response.json();
        document.getElementById('add-response').value = JSON.stringify(responseText, null, 2);
        if (response.ok) {
            alert('Agent added successfully!');
        } else {
            alert('Failed to add agent: ' + JSON.stringify(responseText, null, 2));
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('add-response').value = `Error: ${error.message}`;
    }
}

async function submitSearch() {
    let query = document.getElementById('search-textbox').value;
    document.getElementById('search-response').value = ''; // Clear response area
    if (!query) {
        query = document.getElementById('search-textbox').placeholder;
    }
    try {
        const response = await fetch(`/agents?query=${encodeURIComponent(query)}`, {
            method: 'GET',
        });
        const responseText = await response.json();
        document.getElementById('search-response').value = JSON.stringify(responseText, null, 2);
        if (response.ok) {
            alert('Search successful!');
        } else {
            alert('Search failed: ' + JSON.stringify(responseText, null, 2));
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('search-response').value = `Error: ${error.message}`;
    }
}

async function submitRate() {
    let content = document.getElementById('rate-textbox').value;
    document.getElementById('rate-response').value = ''; // Clear response area
    if (!content) {
        content = document.getElementById('rate-textbox').placeholder;
    }
    try {
        const response = await fetch('/ratings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-yaml',
            },
            body: content,
        });
        const responseText = await response.json();
        document.getElementById('rate-response').value = JSON.stringify(responseText, null, 2);
        if (response.ok) {
            alert('Rating submitted successfully!');
        } else {
            alert('Failed to submit rating: ' + JSON.stringify(responseText, null, 2));
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('rate-response').value = `Error: ${error.message}`;
    }
}

async function submitInvoke() {
    let content = document.getElementById('invoke-textbox').value;
    document.getElementById('invoke-response').value = ''; // Clear response area
    if (!content) {
        content = document.getElementById('invoke-textbox').placeholder;
    }

    // Construct the JSON object with the input topic
    const payload = {
        'input': {
            'topic': content
        }
    };

    try {
        const response = await fetch('/joke/invoke', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        const responseText = await response.json();
        document.getElementById('invoke-response').value = JSON.stringify(responseText, null, 2);
        if (response.ok) {
            alert('Invoke successful!');
        } else {
            alert('Failed to invoke: ' + JSON.stringify(responseText, null, 2));
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('invoke-response').value = `Error: ${error.message}`;
    }
}
