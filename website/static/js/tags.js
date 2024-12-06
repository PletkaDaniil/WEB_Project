function redirectToTagPage() {
    const searchInput = document.getElementById('mySearch').value.trim();
  
    if (searchInput === '') {
      alert('Please enter a tag to search for.');
      return false;
    }
  
    const formattedTag = searchInput.startsWith('#') ? searchInput.slice(1) : searchInput;
    window.location.href = `/tags/${encodeURIComponent(formattedTag)}`;
    return false;
  }