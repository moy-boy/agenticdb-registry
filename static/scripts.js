function setPlaceholderText() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        if (textarea.value.trim() === '') {
            textarea.value = textarea.placeholder;
        }
    });
}

function showLoadingSpinner() {
    document.getElementById('loading-overlay').style.display = 'block';
    document.getElementById('loading-spinner').style.display = 'block';
}

function hideLoadingSpinner() {
    document.getElementById('loading-overlay').style.display = 'none';
    document.getElementById('loading-spinner').style.display = 'none';
}

async function submitAdd() {
    let content = document.getElementById('add-textbox').value;
    document.getElementById('add-response').value = ''; // Clear response area
    if (!content) {
        content = document.getElementById('add-textbox').placeholder;
    }
    showLoadingSpinner();
    try {
        // Parse the content to ensure it's valid JSON
        const parsedContent = JSON.parse(content);
        const response = await fetch('/agents', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(parsedContent),
        });
        const responseText = await response.json();
        if (response.ok) {
            alert('Agent added successfully!');
            document.getElementById('add-response').value = JSON.stringify(responseText, null, 2);
        } else {
            alert('Failed to add agent: ' + JSON.stringify(responseText, null, 2));
            document.getElementById('add-response').value = JSON.stringify(responseText, null, 2);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('add-response').value = `Error: ${error.message}`;
    } finally {
        hideLoadingSpinner();
    }
}

async function submitSearch() {
    let query = document.getElementById('search-textbox').value;
    document.getElementById('search-response').value = ''; // Clear response area
    if (!query) {
        query = document.getElementById('search-textbox').placeholder;
    }
    showLoadingSpinner();
    try {
        const response = await fetch(`/agents?query=${encodeURIComponent(query)}`, {
            method: 'GET',
        });
        const responseText = await response.json();
        if (response.ok) {
            document.getElementById('search-response').value = responseText.agents ? responseText.agents : JSON.stringify(responseText, null, 2);
        } else {
            alert('Search failed: ' + JSON.stringify(responseText, null, 2));
            document.getElementById('search-response').value = JSON.stringify(responseText, null, 2);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('search-response').value = `Error: ${error.message}`;
    } finally {
        hideLoadingSpinner();
    }
}

async function submitRate() {
    let content = document.getElementById('rate-textbox').value;
    document.getElementById('rate-response').value = ''; // Clear response area
    if (!content) {
        content = document.getElementById('rate-textbox').placeholder;
    }
    showLoadingSpinner();
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
            document.getElementById('rate-response').value = JSON.stringify(responseText, null, 2);
        } else {
            alert('Failed to submit rating: ' + JSON.stringify(responseText, null, 2));
            document.getElementById('rate-response').value = JSON.stringify(responseText, null, 2);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('rate-response').value = `Error: ${error.message}`;
    } finally {
        hideLoadingSpinner();
    }
}

async function submitInvoke() {
    let content = document.getElementById('invoke-textbox').value;
    document.getElementById('invoke-response').value = ''; // Clear response area

    try {
        const jsonContent = JSON.parse(content);
        const url = jsonContent.url;
        const payload = { input: jsonContent.input };
        showLoadingSpinner();

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        const responseText = await response.json();
        if (response.ok) {
            document.getElementById('invoke-response').value = responseText.output.result.output;
        } else {
            alert('Failed to invoke: ' + JSON.stringify(responseText, null, 2));
            document.getElementById('invoke-response').value = JSON.stringify(responseText, null, 2);
        }
    } catch (error) {
        alert('Error: ' + error.message);
        document.getElementById('invoke-response').value = `Error: ${error.message}`;
    } finally {
        hideLoadingSpinner();
    }
}