function turnMotor(all){
	var stepsz = document.getElementById('stepSz').value;
    var cId = document.getElementById('cId').value;
    var command = 'step ' + stepsz + ' on Client: ' + cId;
    fetch('/commandClient', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: command
    }).then(response => response.text())
    .then(data => { document.getElementById('testSection').innerText = data;
                    console.log(data);
    });
    if (all){
		return
	} else {
		addRow("motor")
	}
}

function oledDisplay(all){
    var word = document.getElementById('displayWord').value;
    var ind = document.getElementById('displayIndex').value;
    var cId = document.getElementById('cId').value;
    var command = 'display ' + ind + " " + word + ' on Client: ' + cId;
    fetch('/commandClient', {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: command
    }).then(response => response.text())
    .then(data => { document.getElementById('testSection').innerText = data;
                    console.log(data);
    });
    if (all){
		return
	} else {
		addRow("display")
	}
}

function updateAll(){
	if (!document.getElementById('cId').value) {
        alert('Id is missing.');
        return;
    } if (!document.getElementById('displayIndex').value){
		alert('Display index missing');
		return
	} if (!document.getElementById('stepSz').value){
		alert('Display step size missing');
		return
	}
	oledDisplay(true)
	turnMotor(true)
	addRow("all")
}
	

function addRow(col) {
    const idInput = document.getElementById('cId').value;
    var motorInput = '';
    var displayText = '';
    
    if (col == "motor"){
		motorInput = `Step Size: ${document.getElementById('stepSz').value}`;
	} else if (col == "display"){
		const displayWord = document.getElementById('displayWord').value;
		const displayIdx = document.getElementById('displayIndex').value;
		displayText = `Displayed: ${displayWord} at ${displayIdx}`;
	} else if (col == "all"){
		motorInput = `Step Size: ${document.getElementById('stepSz').value}`;
		const displayWord = document.getElementById('displayWord').value;
		const displayIdx = document.getElementById('displayIndex').value;
		displayText = `Displayed: ${displayWord} at ${displayIdx}`;
	}

    if (!idInput) {
        alert('Id is missing.');
        return;
    }

    const tableBody = document.querySelector('#dynamic-table tbody');

    // Create a new row
    const newRow = document.createElement('tr');

    // Create cells for the new row
    const timeCell = document.createElement('td');
    timeCell.textContent = (new Date()).toString().split(' GMT',1)[0];
    newRow.appendChild(timeCell);

    const idCell = document.createElement('td');
    idCell.textContent = idInput;
    newRow.appendChild(idCell);

    const motorCell = document.createElement('td');
    motorCell.textContent = motorInput;
    newRow.appendChild(motorCell);

    const displayCell = document.createElement('td');
    displayCell.textContent = displayText;
    newRow.appendChild(displayCell);

    // Insert the new row at the top
    tableBody.insertBefore(newRow, tableBody.firstChild);

    // Clear the input fields
    document.getElementById('stepSz').value = '';
    document.getElementById('displayWord').value = '';
    document.getElementById('displayIndex').value = '';
}
