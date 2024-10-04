document.addEventListener("DOMContentLoaded", function() {
    var contentDiv = document.getElementById("content");
    var initialContent = contentDiv.innerHTML;

    // Get all list items within the option list
    var optionListItems = document.querySelectorAll("#optionList li");

    // Add click event listener to each list item
    optionListItems.forEach(function(listItem) {
        listItem.addEventListener("click", function() {
            var selectedOption = this.innerText.trim(); // Get the text content of the clicked list item
            contentDiv.innerHTML = ''; // Clear the content div

            switch(selectedOption) {
                case "HOME":
                    contentDiv.innerHTML = initialContent;
                    break;
                case "Add Profile":
                    contentDiv.innerHTML = `
                        <form id="reportForm">
                        <div class="form-row">
                            <div class="form-column">
                            <label for="firstName">First Name</label>
                            <input type="text" class="form-control" id="firstName" placeholder="First name" aria-label="First name">
                            </div>
                            <div class="form-column">
                            <label for="middleInitial">Middle Initial</label>
                            <input type="text" class="form-control" id="middleInitial" placeholder="Middle Initial" aria-label="Middle Initital" required>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-column">
                            <label for="surname">Last Name</label>
                            <input type="text" class="form-control" id="surname" placeholder="Surname" arial-label="Surname" required>
                            </div>
                            <div class="form-column">
                            <label for="birthDate">Birth Date</label>
                            <input type="date" class="form-control" id="birthDate" placeholder="Birth Date" arial-label="Birth Date" required>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-column">
                            <label for="address">Address</label>
                            <input type="text" class="form-control" id="address" placeholder="Address" arial-label="Address" required>
                            </div>
                            <div class="form-column">
                            <label for="gmail">Gmail (Ex. cordovabrant@gmail.com)</label>
                            <input type="email" class="form-control" id="gmail" placeholder="Gmail" arial-label="Gmail" required>
                            </div>
                        </div>
                        
                        <div class="form-row">
                            <div class="form-column">
                            <label for="studentNumber">Student Number (Ex. 202211764)</label>
                            <input type="number" class="form-control" id="studentNumber" placeholder="Student Number" arial-label="Student Number" required>
                            </div>
                            <div class="form-column">
                            <label for="gender">Gender</label>
                            <input type="text" class="form-control" id="gender" placeholder="Gender" arial-label="Gender" required>
                            </div>
                        </div>
                        
                        <button type="button" id="submitButton">Submit</button>
                        </form>
                        `;
                    break;
                case "Add Staff":
                    contentDiv.innerHTML = `
                    <br>
                    <br>
                    <br>
                    <br>
                    <br>
                    <form id="addStaffForm">
                        <div class="StaffForm">
                            <div class="form-column">
                            <label for="userName">Username</label>
                            <input type="text" class="form-control" id="username" placeholder="Username" aria-label="userName">
                            </div>
                            <div class="form-column">
                            <label for="password">Password</label>
                            <input type="password" class="form-control" id="password" placeholder="Password" aria-label="Password" required>
                            </div>
                            <div class="form-column">
                             <label for="section_and_department">Section_and_Department(EX: Computer Science 2-5)</label>
                            <input type="text" class="form-control" id="section_and_department" placeholder="Section and Department" aria-label="Section and Department" required>
                            </div>
                            <button type="button" id="registerStaffButton">Register Staff</button>
                        </div>
                        </form>

                        <!-- Container for error and success messages -->
                        <div id="staffMessageContainer"></div>`;
                    // Event listener for registering staff
                    document.getElementById("registerStaffButton").addEventListener("click", function() {
                        registerStaff();
                    });
                    break;
                case "PROFILES":
                    window.location.href = '/update';
                    break;
                case "RESPOND":
                    fetchReports();
                    break;
                default:
                    console.log("Unknown option selected");
                    break;
            }
        });
    });

    // Event listener for the submit button
    contentDiv.addEventListener("click", function(event) {
        if (event.target && event.target.id == "submitButton") {
            submitAdminForms();
        } else if (event.target && event.target.id == "returnButton") {
            showProfilesButton(); // Display the "Show Profiles" button when "Return" is clicked
        }
    });
});


function registerStaff() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    var section_and_department = document.getElementById('section_and_department').value;
    // Check if any required field is empty
    if (!username || !password ||!section_and_department) {
        showMessageNotification("Please fill in all required fields.");
        return; // Stop form submission if any required field is empty
    }

    var formData = {
        username: username,
        password: password,
        section_and_department
    };

    // Send POST request to register staff
    fetch('/registerStaff', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        if (data.status === 'success') {
            showMessageNotification("Staff registered successfully!");
            console.log(data);
        } else {
            showMessageNotification(data.message);
        }
        addStaffForm.reset()

    })
    .catch(error => {
        console.error('Error submitting form:', error);
        showMessageNotification("An error occurred. Please try again.");
    });
}



function showMessageNotification(message) {
    var notification = document.createElement("div");
    notification.className = "notification";
    notification.textContent = message;

    document.body.appendChild(notification); // Ensure the notification is added to the body

    setTimeout(function() {
        notification.remove(); // Remove the notification after a certain time
    }, 3000);
}


function submitAdminForms() {
    // Retrieve form data
    var formData = {
        firstName: document.getElementById("firstName").value,
        middleInitial: document.getElementById("middleInitial").value,
        surname: document.getElementById("surname").value,
        birthDate: document.getElementById("birthDate").value,
        gender: document.getElementById("gender").value,
        address: document.getElementById("address").value,
        gmail: document.getElementById("gmail").value,
        studentNumber: parseInt(document.getElementById("studentNumber").value) || 0 // Default to 0 if null or NaN
    };

    // Check if any required field is empty
    for (var key in formData) {
        if (formData.hasOwnProperty(key)) {
            if (!formData[key]) {
                showMessageNotification("Please fill in all required fields.");
                return; // Stop form submission if any required field is empty
            }
        }
    }

    // Send POST request to the server if all required fields are filled
    fetch('/submitAdminForms', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            formData: formData
        })
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        // Handle success
        showMessageNotification("Form submitted successfully!");
        console.log(data);
        reportForm.reset()
    })
    .catch(error => {
        // Handle error
        console.error('Error submitting form:', error);
        showMessageNotification("A profile with the same name, email, or student number already exists.");
    });
}



function fetchReports() {
    fetch('/getUserReports', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => displayReports(data))
    .catch(error => {
        console.error('Error fetching reports:', error);
    });
}

function displayReports(reports) {
    var contentDiv = document.getElementById("content");
    if (reports.length === 0) {
        contentDiv.innerHTML = '<p>No reports found.</p>';
        return;
    }

    var acceptedReports = reports.filter(report => report.hasResponse);
    var otherReports = reports.filter(report => !report.hasResponse);

    var selectionBoxHtml = `
        <select id="reportTypeSelection" onchange="toggleReportType()">
            <option value="accepted">Accepted Reports</option>
            <option value="other">Other Reports</option>
        </select>`;

    var acceptedReportsHtml = `
        <div id="acceptedReports" class="report-section">
            <h2>Accepted Reports</h2>
            <table id="acceptedReportsTable">
                <thead>
                    <tr>
                        <th>Incident Date</th>
                        <th>Location</th>
                        <th>Type</th>
                        <th>Relation to Incident</th>
                        <th>Submitted Report Date</th>
                    </tr>
                </thead>
                <tbody>`;

    acceptedReports.forEach(report => {
        acceptedReportsHtml += `
            <tr class="report-row">
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.incident_date}</td>
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.location}</td>
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.type}</td>
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.relation_to_incident}</td>
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.person_date}</td>
            </tr>
            <tr id="case_details_${report.incident_id}" class="case-details" style="display: none;">
                <td colspan="5">
                    <strong>Case Details:</strong>
                    <p>${report.case_details}</p>
                    <div id="responses_${report.incident_id}">
                        <strong>Responses:</strong>
                        <p>Loading responses...</p>
                    </div>
                    <button id="buttonReport" onclick="fetchReports()">Back to Reports</button>
                </td>
            </tr>`;
    });

    acceptedReportsHtml += `
                </tbody>
            </table>
        </div>`;

    var otherReportsHtml = `
        <div id="otherReports" class="report-section" style="display: none;">
            <h2>Other Reports</h2>
            <table id="otherReportsTable">
                <thead>
                    <tr>
                        <th>Incident Date</th>
                        <th>Location</th>
                        <th>Type</th>
                        <th>Relation to Incident</th>
                        <th>Submitted Report Date</th>
                    </tr>
                </thead>
                <tbody>`;

    otherReports.forEach(report => {
        var readClass = report.read ? 'report-read-true' : 'report-read-false'; // Determine class based on read status
        otherReportsHtml += `
            <tr class="report-row ${readClass}">
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.incident_date}</td>
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.location}</td>
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.type}</td>
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.relation_to_incident}</td>
                <td onclick="toggleCaseDetails(${report.incident_id})">${report.person_date}</td>
            </tr>
            <tr id="case_details_${report.incident_id}" class="case-details" style="display: none;">
                <td colspan="5">
                    <strong>Case Details:</strong>
                    <p>${report.case_details}</p>
                    <div id="responses_${report.incident_id}">
                        <strong>Responses:</strong>
                        <p>Loading responses...</p>
                    </div>
                    <div class="report-actions">
                        <input type="text" name="response_${report.incident_id}" id="response_${report.incident_id}" class="response-input" placeholder="Enter response" required>
                        <button type="button" id="buttonSubmit" onclick="submitSingleResponse(${report.incident_id})" class="submit-response-button">Submit</button>
                    </div>
                    <button id="buttonReport" onclick="fetchReports()">Back to Reports</button>
                </td>
            </tr>`;
    });

    otherReportsHtml += `
                </tbody>
            </table>
        </div>`;

    contentDiv.innerHTML = selectionBoxHtml + acceptedReportsHtml + otherReportsHtml;

}




function toggleReportType() {
    var selection = document.getElementById('reportTypeSelection').value;
    var acceptedReports = document.getElementById('acceptedReports');
    var otherReports = document.getElementById('otherReports');

    if (selection === 'accepted') {
        acceptedReports.style.display = 'block';
        otherReports.style.display = 'none';
    } else {
        acceptedReports.style.display = 'none';
        otherReports.style.display = 'block';
    }
}

function toggleCaseDetails(reportId) {
    var acceptedTable = document.getElementById('acceptedReportsTable');
    var otherTable = document.getElementById('otherReportsTable');

    // Function to hide all rows except the selected report's details
    function toggleRows(table, reportId) {
        var rows = table ? table.getElementsByTagName('tr') : [];
        for (var i = 0; i < rows.length; i++) {
            var row = rows[i];
            if (row.id === 'case_details_' + reportId) {
                row.style.display = 'table-row'; // Show the selected report's details
            } else {
                row.style.display = 'none'; // Hide all other rows
            }
        }
    }

    toggleRows(acceptedTable, reportId);
    toggleRows(otherTable, reportId);

    // Fetch and display responses for the selected report
    fetch(`/getResponses/${reportId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            var responsesDiv = document.getElementById('responses_' + reportId);
            if (responsesDiv) {
                if (data.responses && data.responses.length > 0) {
                    responsesDiv.innerHTML = data.responses.map(response =>
                        `<p><strong>${response.responder}:</strong> ${response.response}</p><p><em>${response.date}</em></p>`
                    ).join('');
                } else {
                    responsesDiv.innerHTML = '<p>No responses from the staff or admin.</p>';
                }
            }
        })
        .catch(error => {
            console.error('Error fetching responses:', error);
            var responsesDiv = document.getElementById('responses_' + reportId);
            if (responsesDiv) {
                responsesDiv.innerHTML = '<p>Error loading responses. Please try again later.</p>';
            }
        });

    // Mark report as read
    fetch(`/markReportAsRead/${reportId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Report marked as read:', data.message);
        // Optionally update UI or perform additional actions upon success
    })
    .catch(error => {
        console.error('Error marking report as read:', error);
        // Handle error scenarios if needed
    });
}


function showAllReports() {
    var acceptedTable = document.getElementById('acceptedReportsTable');
    var otherTable = document.getElementById('otherReportsTable');
    var acceptedRows = acceptedTable ? acceptedTable.getElementsByTagName('tr') : [];
    var otherRows = otherTable ? otherTable.getElementsByTagName('tr') : [];

    // Toggle display of all accepted report rows
    for (var i = 0; i < acceptedRows.length; i++) {
        var row = acceptedRows[i];
        if (row.classList.contains('case-details')) {
            row.style.display = 'none'; // Hide case details rows
        } else {
            row.style.display = row.style.display === 'none' ? 'table-row' : 'none'; // Toggle display
        }
    }
    
    // Toggle display of all other report rows
    for (var i = 0; i < otherRows.length; i++) {
        var row = otherRows[i];
        if (row.classList.contains('case-details')) {
            row.style.display = 'none'; // Hide case details rows
        } else {
            row.style.display = row.style.display === 'none' ? 'table-row' : 'none'; // Toggle display
        }
    }
}






function submitSingleResponse(incidentId) {
    var responseElement = document.getElementById(`response_${incidentId}`);

    // Check if element exists
    if (!responseElement) {
        showMessageNotification("Response input not found.");
        return;
    }

    var response = responseElement.value;

    // Check if response is empty
    if (!response) {
        showMessageNotification("Please fill in the response field.");
        return;
    }

    var formData = {
        response: response,
        incident_id: incidentId
    };

    // Send form data to server
    fetch('/submitResponseForm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ formData: formData })
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Parse the response as JSON
        }
        return response.json().then(errorData => {
            throw new Error(errorData.error || 'Network response was not ok.');
        });
    })
    .then(data => {
        console.log(data); // Handle success response
        showMessageNotification("Response submitted successfully!"); // Display success message
        // Optionally, redirect to another page or update UI
    })
    .catch(error => {
        console.error('Error submitting form:', error); // Handle error
        showMessageNotification("An error occurred. Please try again."); // Display error message
    });
}



function submitSingleResponse(incidentId) {
    var responseElement = document.getElementById(`response_${incidentId}`);

    // Check if element exists
    if (!responseElement) {
        showMessageNotification("Response input not found.");
        return;
    }

    var response = responseElement.value;

    // Check if response is empty
    if (!response) {
        showMessageNotification("Please fill in the response field.");
        return;
    }

    var formData = {
        response: response,
        incident_id: incidentId
    };

    // Send form data to server
    fetch('/submitResponseForm', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ formData: formData })
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Parse the response as JSON
        }
        return response.json().then(errorData => {
            throw new Error(errorData.error || 'Network response was not ok.');
        });
    })
    .then(data => {
        console.log(data); // Handle success response
        showMessageNotification("Response submitted successfully!"); // Display success message
        // Optionally, redirect to another page or update UI
    })
    .catch(error => {
        console.error('Error submitting form:', error); // Handle error
        showMessageNotification("An error occurred. Please try again."); // Display error message
    });
}


