function redirectToTagPage() {
  const searchInput = document.getElementById('mySearch').value.trim();

  if (searchInput === '') {
    showFlashMessage('Please enter a tag to search for.', 'error');
    return false;
  }

  const formattedTag = searchInput.startsWith('#') ? searchInput.slice(1) : searchInput;
  window.location.href = `/tags/${encodeURIComponent(formattedTag)}`;
  return false;
}

let errorTimeout;
function showFlashMessage(message) {
    const errorContainer = document.getElementById('error-output');

    if (!errorContainer) {
        console.error('Error container not found in the DOM.');
        return;
    }

    errorContainer.innerHTML = `<p class="error-message">${message}</p>`;
    errorContainer.style.display = 'flex';
    errorContainer.classList.add('fadeInUp');

    if (errorTimeout) {
        clearTimeout(errorTimeout);
    }

    errorTimeout = setTimeout(() => {
        errorContainer.style.display = 'none';
        errorContainer.classList.remove('fadeInUp');
        errorContainer.innerHTML = '';
    }, 3000);
}
