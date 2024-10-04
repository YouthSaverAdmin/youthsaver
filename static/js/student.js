document.addEventListener("DOMContentLoaded", function() {
    var dropdown = document.getElementById("reportOptions"); // Changed ID to match HTML
    var contentDiv = document.getElementById("content");
    var initialContent = contentDiv.innerHTML;
    
    dropdown.addEventListener("click", function(event) { // Changed event to 'click'
        var selectedOption = event.target.getAttribute("data-value"); // Get the data-value attribute of the clicked item
        contentDiv.innerHTML = ''; // Clear the content
        
        switch(selectedOption) {
            case "home":
                contentDiv.innerHTML = initialContent;
                break;
            case "REPORT":
                contentDiv.innerHTML = `
                    <form id="reportForm" >
                    <label for="incidentDate">Incident Date:</label>
                    <input type="date" id="incidentDate" name="incidentDate" required>
                    
                    <label for="caseDetails">Case Details:</label>
                    <textarea type="text" id="caseDetails" name="caseDetails" placeholder="Enter Case Details" required></textarea>
                    
                    <label for="location">Location:</label>
                    <input type="text" id="location" name="location" placeholder="Enter Location" required>
                    
                    <label for="type">Type:</label>
                    <select id="type" name="type" onchange="showOtherTypeInput()" required>
                        <option value="bullying">Bullying</option>
                        <option value="harassment">Harassment</option>
                        <option value="extortion">Extortion</option>
                        <option value="cyber_bullying">Cyber Bullying</option>
                        <option value="other">Other</option>
                    </select>
                    
                    <div id="otherTypeInput" style="display: none;">
                        <label for="otherType">Other Type:</label>
                        <input type="text" id="otherType" name="otherType" placeholder="Enter Other Type" class="wide-input">
                    </div>
                    
                    <label for="relationToIncident">Relation to Incident:</label>
                    <input type="text" id="relationToIncident" name="relationToIncident" placeholder="Enter Relation to Incident" required>
                    
                    <button type="button" id="submitButton">Submit</button>
            </form>`;
                break;
            case "read":
                fetchReports();
                break;
            default:
                console.log("Unknown option selected");
                break;
        }
    });

  
    // Event listener for the submit button
    document.getElementById("content").addEventListener("click", function(event) {
        if (event.target && event.target.id == "submitButton") {
            submitForm();
        } else if (event.target && event.target.classList.contains("responsesButton")) {
            var incidentId = event.target.getAttribute("data-incident-id");
            fetchResponses(incidentId);
        }
    });
});




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

    // Sort reports by incident_date (assuming incident_date is in ISO 8601 format)
    reports.sort((a, b) => new Date(a.incident_date) - new Date(b.incident_date));

    var otherReportsHtml = `
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

    // Fetch responses for each report asynchronously
    Promise.all(reports.map(report =>
        fetch(`/getResponses/${report.incident_id}`)
            .then(response => response.json())
            .then(data => {
                report.read = data.read; // Assign read status from server response
                report.responses = data.responses; // Assign responses for further processing if needed
            })
            .catch(error => {
                console.error('Error fetching responses:', error);
                report.read = false; // Assume unread if fetching fails
            })
    ))
    .then(() => {
        // After marking read statuses and sorting, generate HTML for reports
        reports.forEach(report => {
            if (report.hasResponse) {
                // Skip reports with responses
                return;
            }
            
            var rowClass = report.read ? 'read-report' : 'unread-report';
            console.log(`Report ${report.incident_id} read status: ${report.read}, applying class: ${rowClass}`);

            otherReportsHtml += `
                <tr class="report-row ${rowClass}" onclick="toggleCaseDetails(${report.incident_id})">
                    <td>${report.incident_date}</td>
                    <td>${report.location}</td>
                    <td>${report.type}</td>
                    <td>${report.relation_to_incident}</td>
                    <td>${report.person_date}</td>
                </tr>
                <tr id="case_details_${report.incident_id}" class="case-details" style="display: none;">
                    <td colspan="5">
                        <strong>Case Details:</strong>
                        <p>${report.case_details}</p>
                        <div id="responses_${report.incident_id}">
                            <strong>Responses:</strong>
                            ${formatResponses(report.responses)}
                        </div>
                        <button onclick="showAllReports()">Back to Reports</button>
                    </td>
                </tr>`;
        });

        otherReportsHtml += `</tbody></table>`;
        contentDiv.innerHTML = otherReportsHtml;
    })
    .catch(error => {
        console.error('Error fetching responses for reports:', error);
        contentDiv.innerHTML = '<p>Error loading reports. Please try again later.</p>';
    });
}



function formatResponses(responses) {
    if (!responses || responses.length === 0) {
        return '<p>No responses</p>';
    }
    var html = '<ul>';
    responses.forEach(response => {
        html += `<li>${response.text} - ${response.date}</li>`;
    });
    html += '</ul>';
    return html;
}

function toggleCaseDetails(reportId) {
    var table = document.getElementById('otherReportsTable');
    var rows = table.getElementsByTagName('tr');

    // Hide all report rows except the one selected
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        if (row.id === 'case_details_' + reportId) {
            row.style.display = 'table-row'; // Show the selected report's details
        } else {
            row.style.display = 'none'; // Hide all other rows
        }
    }

    // Fetch and display responses for the selected report
    fetch(`/getResponses/${reportId}`)
        .then(response => response.json())
        .then(data => {
            var responsesDiv = document.getElementById('responses_' + reportId);
            if (data.responses && data.responses.length > 0) {
                responsesDiv.innerHTML = data.responses.map(response =>
                    `<p><strong>${response.responder}:</strong> ${response.response}</p><p><em>${response.date}</em></p>
                    <br>
                    <br>
                   
                    <p><strong>The Guidance is located at ground floor:</strong> </p>
                    <p><strong>Morning time 10 to 12</strong> </p>
                    <p><strong>Afternoon time 2 to 5</strong> </p>
                    <p><strong>Open during Monday to thursday</strong> </p>
                    <p><strong>feel free to come in during our available hours</strong> </p>`
                    
                ).join('');

                // Add button for accepting responses
                responsesDiv.innerHTML += `<button id="acceptResponse" onclick="acceptResponses(${reportId})">Accept Responses</button>`;
            } else {
                responsesDiv.innerHTML = '<p>No responses from the staff or admin.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching responses:', error);
            var responsesDiv = document.getElementById('responses_' + reportId);
            responsesDiv.innerHTML = '<p>Error loading responses. Please try again later.</p>';
        });

    // Mark the report as read
    markAsRead(reportId);
}

function showAllReports() {
    var table = document.getElementById('otherReportsTable');
    var rows = table.getElementsByTagName('tr');

    // Show all report rows and hide case details rows
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        if (row.classList.contains('case-details')) {
            row.style.display = 'none'; // Hide case details rows
        } else {
            row.style.display = 'table-row'; // Show report rows
        }
    }
}



function markAsRead(incident_id) {
    fetch(`/markResponseAsRead/${incident_id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            // Update the report row to reflect the read status
            var reportRow = document.querySelector(`.report-row[onclick='toggleCaseDetails(${incident_id})']`);
            if (reportRow) {
                reportRow.classList.remove('unread-report');
                reportRow.classList.add('read-report');
            }
        } else {
            console.error('Error marking report as read:', data.error);
        }
    })
    .catch(error => {
        console.error('Error marking report as read:', error);
    });
}




function acceptResponses(reportId) {
    fetch('/acceptResponseNotification', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ incident_id: reportId }),
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Failed to send notification.');
    })
    .then(data => {
        showMessageNotification('Response accepted successfully!');
        goBack()
    })
    .catch(error => {
        console.error('Error accepting response:', error);
        alert('Error accepting response. Please try again.');
    });
}




 
function goBack() {
   
  fetchReports(); // Assuming this function displays reports
        
    
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




// Function to show/hide other type input based on selected option
function showOtherTypeInput() {
    var type = document.getElementById("type").value;
    var otherTypeInput = document.getElementById("otherTypeInput");
    if (type === "other") {
        otherTypeInput.style.display = "block";
    } else {
        otherTypeInput.style.display = "none";
    }
}
function submitForm() {
    var formData = {};

    // Populate formData based on the selected option directly
    var selectedOption = "REPORT"; // Assuming "REPORT" is the default option
    
    switch(selectedOption) {
        case "REPORT":
            formData = {
                incidentDate: document.getElementById("incidentDate").value.trim(),
                caseDetails: document.getElementById("caseDetails").value.trim(),
                location: document.getElementById("location").value.trim(),
                type: document.getElementById("type").value.trim(),
                // Include Other Type value if type is 'other'
                otherType: document.getElementById("type").value.trim() === "other" ? 
                          document.getElementById("otherType").value.trim() : "",
                relationToIncident: document.getElementById("relationToIncident").value.trim()
            };

            // Check if any required field is empty
            var requiredFields = ["incidentDate", "caseDetails", "location", "type", "relationToIncident"];
            for (var i = 0; i < requiredFields.length; i++) {
                var field = requiredFields[i];
                if (formData[field] === "") {
                    showMessageNotification("Please fill in all required fields.");
                    return; // Stop form submission
                }
            }
            break;
        case "home":
        case "read":
            // No additional fields to include
            break;
        default:
            console.log("Unknown option selected");
            return;
    }

    // Send POST request to the server
    fetch('/submitForms', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            collectionName: 'Incidents', // Change collection name as needed
            formData: formData
        })
    })
    .then(response => {
        if (response.ok) {
            showMessageNotification("Form submitted successfully.");
            return response.text();
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        // Handle success
        console.log(data);
        reportForm.reset();
    })
    .catch(error => {
        // Handle error
        console.error('Error submitting form:', error);
        showMessageNotification("Report not submitted. Please try again later.");
    });
}
