function updateTable() {
    const tbody = document.querySelector('#data-table tbody');
    tbody.innerHTML = ''; // Clear the table body
    data.forEach((item) => {
        tbody.insertAdjacentHTML('beforeend', row);
    });
}
function fetchData() {
    fetch('/fetchData').then(response => response.json())
        .then(data => {
            let table = document.getElementById('data-table');
            table.innerHTML = '';
            data.forEach(row => {
                let tr = document.createElement('tr');
                Object.values(row).forEach(value => {
                    let td = document.createElement('td')
                    td.textContent = value;
                    tr.appendChild(td);
                });
                table.appendChild(tr);
            });
        });
}

setInterval(fetchData, 5000); // Fetch every 5 seconds
