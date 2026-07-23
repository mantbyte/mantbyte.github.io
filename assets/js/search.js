let searchData = [];
let searchOverlay = document.getElementById('search-overlay');
let searchInput = document.getElementById('search-input');
let searchResults = document.getElementById('search-results');

// Fetch search index
fetch('/search.json')
    .then(response => response.json())
    .then(data => {
        searchData = data;
    })
    .catch(error => console.error('Error fetching search data:', error));

function toggleSearch() {
    if (!searchOverlay) return;
    
    searchOverlay.classList.toggle('active');
    if (searchOverlay.classList.contains('active')) {
        setTimeout(() => searchInput.focus(), 100);
    } else {
        searchInput.value = '';
        searchResults.innerHTML = '';
    }
}

// Simple search logic
if (searchInput) {
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        searchResults.innerHTML = '';
        
        if (query.length < 2) return;
        
        const results = searchData.filter(post => {
            return (post.title && post.title.toLowerCase().includes(query)) ||
                   (post.content && post.content.toLowerCase().includes(query)) ||
                   (post.category && post.category.toLowerCase().includes(query));
        }).slice(0, 10); // Limit to 10 results
        
        if (results.length === 0) {
            searchResults.innerHTML = '<li><p>No posts found.</p></li>';
            return;
        }
        
        results.forEach(post => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="${post.url}">${post.title}</a>
                <p>${post.excerpt}</p>
            `;
            searchResults.appendChild(li);
        });
    });
}
