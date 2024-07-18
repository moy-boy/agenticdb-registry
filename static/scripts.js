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
        if (response.ok) {
            alert('Agent added successfully!');
            document.getElementById('add-textbox').value += `\n\nResponse:\n${JSON.stringify(responseText, null, 2)}`;
        } else {
            alert('Failed to add agent: ' + JSON.stringify(responseText, null, 2));
            document.getElementById('add-textbox').value += `\n\nError:\n${JSON.stringify(responseText, null, 2)}`;
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('add-textbox').value += `\n\nError:\n${error.message}`;
    }
}

async function submitSearch() {
    let query = document.getElementById('search-textbox').value;
    if (!query) {
        query = document.getElementById('search-textbox').placeholder;
    }
    try {
        const response = await fetch(`/agents?query=${encodeURIComponent(query)}`, {
            method: 'GET',
        });
        const responseText = await response.json();
        if (response.ok) {
            document.getElementById('search-textbox').value += `\n\nResponse:\n${JSON.stringify(responseText, null, 2)}`;
            alert('Search successful: ' + JSON.stringify(responseText, null, 2));
        } else {
            alert('Search failed: ' + JSON.stringify(responseText, null, 2));
            document.getElementById('search-textbox').value += `\n\nError:\n${JSON.stringify(responseText, null, 2)}`;
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('search-textbox').value += `\n\nError:\n${error.message}`;
    }
}

async function submitRate() {
    let content = document.getElementById('rate-textbox').value;
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
        if (response.ok) {
            alert('Rating submitted successfully!');
            document.getElementById('rate-textbox').value += `\n\nResponse:\n${JSON.stringify(responseText, null, 2)}`;
        } else {
            alert('Failed to submit rating: ' + JSON.stringify(responseText, null, 2));
            document.getElementById('rate-textbox').value += `\n\nError:\n${JSON.stringify(responseText, null, 2)}`;
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('rate-textbox').value += `\n\nError:\n${error.message}`;
    }
}

async function submitInvoke() {
    let content = document.getElementById('invoke-textbox').value;
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
        if (response.ok) {
            alert('Invoke successful!');
            document.getElementById('invoke-textbox').value += `\n\nResponse:\n${JSON.stringify(responseText, null, 2)}`;
        } else {
            alert('Failed to invoke: ' + JSON.stringify(responseText, null, 2));
            document.getElementById('invoke-textbox').value += `\n\nError:\n${JSON.stringify(responseText, null, 2)}`;
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('invoke-textbox').value += `\n\nError:\n${error.message}`;
    }
}
