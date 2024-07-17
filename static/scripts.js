async function submitAdd() {
    const content = document.getElementById('add-textbox').value;
    try {
        const response = await fetch('/agents', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-yaml',
            },
            body: content,
        });
        if (response.ok) {
            alert('Agent added successfully!');
        } else {
            const errorText = await response.text();
            alert('Failed to add agent: ' + errorText);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function submitSearch() {
    const query = document.getElementById('search-textbox').value;
    try {
        const response = await fetch(`/agents?query=${encodeURIComponent(query)}`, {
            method: 'GET',
        });
        if (response.ok) {
            const result = await response.json();
            alert('Search successful: ' + JSON.stringify(result, null, 2));
        } else {
            const errorText = await response.text();
            alert('Search failed: ' + errorText);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function submitRate() {
    const content = document.getElementById('rate-textbox').value;
    try {
        const response = await fetch('/ratings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-yaml',
            },
            body: content,
        });
        if (response.ok) {
            alert('Rating submitted successfully!');
        } else {
            const errorText = await response.text();
            alert('Failed to submit rating: ' + errorText);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function submitInvoke() {
    const content = document.getElementById('invoke-textbox').value;
    try {
        const response = await fetch('/joke/invoke', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-yaml',
            },
            body: content,
        });
        if (response.ok) {
            alert('Invoke successful!');
        } else {
            const errorText = await response.text();
            alert('Failed to invoke: ' + errorText);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}
