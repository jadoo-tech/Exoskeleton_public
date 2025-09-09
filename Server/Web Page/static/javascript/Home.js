// Handle login button click
document.getElementById('login-button').addEventListener('click', function() {
    // TODO: Replace this with actual login logic
    document.getElementById('login-container').innerHTML = `
        <button id="dropdown-button">Menu ▼</button>
        <div id="dropdown-menu">
            <a href="/dataDisplay">View Data</a>
            <a href="/motionControls">Motion Control</a>
            <a href="404Error">Data Analysis</a>
            <a href="#" id="logout-button">Logout</a>
        </div>
    `;
    
    // Add event listeners for new buttons
    document.getElementById('dropdown-button').addEventListener('click', toggleDropdown);
    document.getElementById('logout-button').addEventListener('click', function() {
        location.reload();  // Simple logout by reloading the page
    });
});

// Toggle dropdown menu
function toggleDropdown() {
    const dropdown = document.getElementById('dropdown-menu');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}
