let isLoggedIn = false; // Track login state
let acceptedJob = null; // Store accepted job info

// Function to toggle the visibility of sections
function toggleSection(sectionId) {
    const section = document.getElementById(sectionId);
    section.style.display = (section.style.display === "none") ? "block" : "none";
}

// Function to dynamically load content based on the section clicked
function loadContent(section) {
    console.log('loadContent called with section:', section);
    const contentContainer = document.getElementById('content-container');
    contentContainer.innerHTML = '';

    if (section === 'flight-log') {
        let acceptedJob = JSON.parse(localStorage.getItem('acceptedJob') || 'null');
        contentContainer.innerHTML = `
            <h2>Flight Log</h2>
            <form id="flightLogForm" method="POST" action="/submit-flight-log">
                <label for="departure">Departure:</label>
                <input type="text" id="departure" name="departure" required value="${acceptedJob ? acceptedJob.departure_airport : ''}"><br><br>
                <label for="destination">Destination:</label>
                <input type="text" id="destination" name="destination" required value="${acceptedJob ? acceptedJob.destination_airport : ''}"><br><br>
                <label for="date">Date:</label>
                <input type="date" id="date" name="date" required><br><br>
                <label for="hours">Flight Hours:</label>
                <input type="number" id="hours" name="hours" step="0.1" required><br><br>
                <label for="pilotId">Pilot ID:</label>
                <input type="text" id="pilotId" name="pilotId" required><br><br>
                <label for="aircraftType">Aircraft Type:</label>
                <input type="text" id="aircraftType" name="aircraftType" required><br><br>
                <label for="aircraftIdent">Aircraft Ident:</label>
                <input type="text" id="aircraftIdent" name="aircraftIdent" required><br><br>
                <label for="flightNumber">Flight Number:</label>
                <input type="text" id="flightNumber" name="flightNumber" required value="${acceptedJob ? acceptedJob.job_id : ''}"><br><br>
                <label for="takeoffsDay">Number of Takeoffs (Day):</label>
                <input type="number" id="takeoffsDay" name="takeoffsDay" required><br><br>
                <label for="takeoffsNight">Number of Takeoffs (Night):</label>
                <input type="number" id="takeoffsNight" name="takeoffsNight" required><br><br>
                <label for="landingsDay">Number of Landings (Day):</label>
                <input type="number" id="landingsDay" name="landingsDay" required><br><br>
                <label for="landingsNight">Number of Landings (Night):</label>
                <input type="number" id="landingsNight" name="landingsNight" required><br><br>
                <label for="instrumentApproach">Number of Instrument Approaches:</label>
                <input type="number" id="instrumentApproach" name="instrumentApproach" required><br><br>
                
                <input type="hidden" id="jobMarketId" name="jobMarketId" value="${acceptedJob ? acceptedJob.jm_id : ''}">

                <button type="submit">Add Flight</button>
            </form>
        `;
    } else if (section === 'logbook') {
        contentContainer.innerHTML = `
            <h2>Logbook</h2>
            <iframe src="/logbook" style="width: 100%; height: 100%; border: none;"></iframe>
        `;
    } else if (section === 'job-market') {
        // Only allow access if logged in
        if (!isLoggedIn) {
            contentContainer.innerHTML = `<p>You must be logged in to view the Job Market.</p>`;
            return;
        }
        console.log('Job Market section reached');
        fetch('http://127.0.0.1:5000/api/job-market')
            .then(response => response.json())
            .then(jobs => {
                console.log('Jobs data received:', jobs);
                let acceptedJob = JSON.parse(localStorage.getItem('acceptedJob') || 'null');
                let pilot = JSON.parse(localStorage.getItem('pilot') || '{}');
                let rankMultipliers = {
                    "CPL 1": 0.7, "CPL 2": 0.75, "CPL 3": 0.8, "CPL 4": 0.85,
                    "CPL 5": 0.9, "CPL 6": 1.0, "CPL 7": 1.05, "CPL 8": 1.1,
                    "CPL 9": 1.15, "CPL 10": 1.2, "CPL 11": 1.3, "CPL 12": 1.5
                };
                let multiplier = rankMultipliers[pilot.rank] || 1.0;

                let jobMarketHTML = `
                    <h2>Job Market</h2>
                    <p>Explore job opportunities to grow your virtual economy!</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Job Market ID</th>
                                <th>Job ID</th>
                                <th>Job Type</th>
                                <th>Job Description</th>
                                <th>Cargo Weight</th>
                                <th>Departure</th>
                                <th>Destination</th>
                                <th>Reward</th>
                                <th>Status</th>
                                <th>Accept</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                jobs.forEach(job => {
    let isAccepted = acceptedJob && acceptedJob.jm_id === job.jm_id;
    let displayReward = Math.round(job.reward * multiplier);
    
    // Determine the content for the passengers/cargo column
    let cargoPassengerInfo = '';
    if (job.job_type === 'Air Taxi') {
        cargoPassengerInfo = `${job.passengers} Passengers`;
    } else if (job.job_type === 'Cargo') {
        cargoPassengerInfo = `${job.cargo_weight} kg`;
    }

    // Determine the content for the description column
    let descriptionText = job.job_description; // Use the correct field from the database
    
    jobMarketHTML += `
        <tr>
            <td>${job.jm_id}</td>
            <td>${job.job_id}</td>
            <td>${job.job_type}</td>
            <td>${job.job_description}</td>
            <td>${cargoPassengerInfo}</td> 
            <td>${job.departure_airport}</td>
            <td>${job.destination_airport}</td>
            <td>${displayReward}€</td>
            <td>${job.status}</td>
            <td>
                <button class="accept-job-btn" data-jmid="${job.jm_id}" data-jobid="${job.job_id}"
                    ${job.status !== 'Available' || isAccepted ? 'disabled' : ''}
                >
                    ${
                        isAccepted
                            ? 'Job Accepted'
                            : (job.status === 'Accepted'
                                ? 'Job Accepted'
                                : (job.status === 'Completed'
                                    ? 'Completed'
                                    : 'Accept'))
                    }
                </button>
            </td>
        </tr>
    `;
});
                contentContainer.innerHTML = jobMarketHTML;
                console.log('Job Market table updated in contentContainer');

                // Add event listeners for Accept buttons
                document.querySelectorAll('.accept-job-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const jmId = btn.getAttribute('data-jmid');
                        const jobId = btn.getAttribute('data-jobid');
                        const job = jobs.find(j => j.jm_id === jmId);
                        if (job && job.status === 'Available') {
                            btn.textContent = 'Job Accepted';
                            btn.disabled = true;
                            acceptedJob = job;
                            localStorage.setItem('acceptedJob', JSON.stringify(acceptedJob));
                            alert(`You accepted job: ${jobId}`);
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Error fetching jobs:', error);
                contentContainer.innerHTML = `<p>Error loading job market data: ${error.message}</p>`;
            });
    } else if (section === 'operations') {
        contentContainer.innerHTML = `
            <h2>Pilots Portal</h2>
            <div id="pilotPortal">
                <h3>Create Pilot Profile</h3>
                <form id="createPilotForm">
                    <label for="pilotName">Name:</label>
                    <input type="text" id="pilotName" name="pilotName" required><br><br>
                    <label for="pilotEmail">Email:</label>
                    <input type="email" id="pilotEmail" name="pilotEmail" required><br><br>
                    <label for="pilotPassword">Password:</label>
                    <input type="password" id="pilotPassword" name="pilotPassword" required><br><br>
                    <button type="button" id="createPilotButton">Create Profile</button>
                </form>
                <hr>
                <h3>Log In</h3>
                <form id="loginPilotForm">
                    <label for="loginEmail">Email:</label>
                    <input type="email" id="loginEmail" name="loginEmail" required><br><br>
                    <label for="loginPassword">Password:</label>
                    <input type="password" id="loginPassword" name="loginPassword" required><br><br>
                    <button type="button" id="loginPilotButton">Log In</button>
                </form>
                <div class="forgot-password-link-container">
                    <a href="#" id="forgot-password-link">Forgot Password?</a>
                </div>
                <div id="reset-password-modal">
                    <div class="modal-content">
                        <h3>Reset Password</h3>
                        <input type="email" id="reset-email" placeholder="Your email">
                        <input type="password" id="reset-new-password" placeholder="New password">
                        <button id="reset-password-btn">Reset Password</button>
                        <button class="cancel-btn" onclick="document.getElementById('reset-password-modal').style.display='none'">Cancel</button>
                    </div>
                </div>
            </div>
        `;
        // Add this line here
    attachOperationsListeners(); 

    } else if (section === 'fleet') {
        // Only allow access if logged in
        if (!isLoggedIn) {
            contentContainer.innerHTML = `<p>You must be logged in to view the Fleet.</p>`;
            return;
        }
        fetch('http://127.0.0.1:5000/api/fleet')
            .then(response => response.json())
            .then(fleet => {
                let pilot = JSON.parse(localStorage.getItem('pilot') || '{}');
                let fleetHTML = `
                    <h2>Aircraft Fleet</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Ident</th>
                                <th>Model</th>
                                <th>Status</th>
                                <th>Pilot</th>
                                <th>Hours Flown</th>
                                <th>A Check</th>
                                <th>B Check</th>
                                <th>C Check</th>
                                <th>Maintenance_Required</th>
                                <th>Mantenance_Cost</th>
                                <th>Book</th>
                                <th>Location</th>
                                <th>Condition (%) </th>
                                <th>Type</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                fleet.forEach(ac => {
                    let canBook = ac.status === 'Free' && !ac.maintenance_required;
                    // Show Repair button if Condition < 100
                    let showRepair = ac.Condition !== undefined && ac.Condition < 100;

                    fleetHTML += `
<tr>
    <td>
        <span class="ident-text" data-ident="${ac.aircraft_ident}">${ac.aircraft_ident}</span>
        <button class="edit-ident-btn" data-ident="${ac.aircraft_ident}" title="Edit Ident">✏️</button>
    </td>
    <td>
        ${ac.description || ac.aircraft_model || ''}
    </td>
    <td>${ac.status}</td>
    <td>${ac.owner_id}</td>
    <td>${ac.Hours_Flown}</td>
    <td>${ac.last_a_check}</td>
    <td>${ac.last_b_check}</td>
    <td>${ac.last_c_check}</td>
    <td>${ac.maintenance_required}</td>
    <td>${ac.maintenance_cost}</td>
    <td>
        <button class="book-aircraft-btn" data-ident="${ac.aircraft_ident}">
            Book
        </button>
    </td>
    <td>${ac.Location || ''}</td>
    <td>
        ${ac.Condition}
        ${showRepair ? `<button class="repair-btn" data-ident="${ac.aircraft_ident}">Repair</button>` : ''}
    </td>
    <td>${ac.type || ''}</td>
</tr>
`;
                });
                fleetHTML += `
                        </tbody>
                    </table>
                `;
                contentContainer.innerHTML = fleetHTML;

                // Add event listeners for Book buttons
                document.querySelectorAll('.book-aircraft-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const ident = btn.getAttribute('data-ident');
                        fetch('http://127.0.0.1:5000/api/fleet/book', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                aircraft_ident: ident,
                                owner_id: pilot.identifier
                            })
                        })
                        .then(res => res.json())
                        .then(result => {
                            if (result.success) {
                                alert(`Aircraft ${ident} booked!`);
                                loadContent('fleet'); // Refresh fleet table
                            } else {
                                alert('Failed to book aircraft.');
                            }
                        });
                    });
                });

                // Add event listeners for Sell buttons
                document.querySelectorAll('.sell-btn').forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const aircraftIdent = this.getAttribute('data-ident');
                        const isLeased = this.getAttribute('data-leased') === 'true';
                        const endpoint = isLeased ? '/api/fleet/return' : '/api/fleet/sell';
                        fetch(endpoint, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ aircraft_ident: aircraftIdent, pilot_id: pilot.identifier })
                        })
                        .then(res => res.json())
                        .then(result => {
                            if (result.success) {
                                if (isLeased) {
                                    alert('Aircraft returned!');
                                } else {
                                    alert(`Aircraft sold for ${result.sale_price}€`);
                                    updatePilotBalance(pilot.balance + result.sale_price);
                                }
                                loadContent('fleet');
                            } else {
                                alert(result.message || 'Sale failed.');
                                alert(result.message || (isLeased ? 'Return failed.' : 'Sale failed.'));
                            }
                        });
                    });
                });

                // Add event listeners for Repair buttons
                document.querySelectorAll('.repair-btn').forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const ident = this.getAttribute('data-ident');
                        fetch('/api/fleet/repair', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ aircraft_ident: ident })
                        })
                        .then(res => res.json())
                        .then(result => {
                            if (result.success) {
                                alert('Aircraft repaired successfully!');
                                loadContent('fleet'); // Refresh fleet content
                            } else {
                                alert('Repair failed: ' + (result.message || 'Unknown error'));
                            }
                        })
                        .catch(error => {
                            alert('Error repairing aircraft: ' + error.message);
                        });
                    });
                });

                // Edit Ident button click handler
                document.querySelectorAll('.edit-ident-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const oldIdent = btn.getAttribute('data-ident');
                        const span = document.querySelector(`.ident-text[data-ident="${oldIdent}"]`);
                        const currentIdent = span.textContent;
                        const input = document.createElement('input');
                        input.type = 'text';
                        input.value = currentIdent;
                        input.size = 8;
                        span.replaceWith(input);
                        input.focus();

                        input.addEventListener('blur', function() {
                            const newIdent = input.value.trim();
                            if (newIdent && newIdent !== oldIdent) {
                                fetch('/api/fleet/update_ident', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ old_ident: oldIdent, new_ident: newIdent })
                                })
                                .then(res => res.json())
                                .then(result => {
                                    if (result.success) {
                                        loadContent('fleet');
                                    } else {
                                        alert('Failed to update Ident.');
                                        loadContent('fleet');
                                    }
                                });
                            } else {
                                loadContent('fleet');
                            }
                        });
                    });
                });
            })
            .catch(error => {
                contentContainer.innerHTML = `<p>Error loading fleet: ${error.message}</p>`;
            });
    } else if (section === 'marketplace') {
        contentContainer.innerHTML = `
            <h2>Marketplace</h2>
            <h3>Aircraft New</h3>
            <div id="new-aircraft-list"></div>
            <h3>Private Sale</h3>
            <div id="private-sale-list"></div>
        `;

        // Aircraft New
        fetch('/api/marketplace/new')
            .then(res => res.json())
            .then(data => {
                let html = `<table>
    <tr>
        <th>Model</th>
        <th>Manufacturer</th>
        <th>Type</th>
        <th>MTOW (kg)</th>
        <th>Price (€)</th>
        <th>Lease Price (€)</th>
    </tr>`;
data.forEach(ac => {
    html += `<tr>
        <td>${ac.description}</td>
        <td>${ac.manufacturer}</td>
        <td>${ac.type}</td>
        <td>${ac.mtow}</td>
        <td>
            ${ac.cost_new}
            <button class="market-btn buy-btn" data-id="${ac.id}" data-type="new">Buy</button>
        </td>
        <td>
            ${ac.lease_price}
            <button class="market-btn lease-btn" data-id="${ac.id}" data-type="new">Lease</button>
        </td>
    </tr>`;
});
                html += '</table>';
                document.getElementById('new-aircraft-list').innerHTML = html;
                attachMarketplaceButtonListeners(); // <-- Attach listeners here!
            });

        // Private Sale
        fetch('/api/marketplace/private')
            .then(res => res.json())
            .then(data => {
                let html = `<table>
        <tr>
            <th>Model</th>
            <th>Manufacturer</th>
            <th>Type</th>
            <th>MTOW (kg)</th>
            <th>Used Price (€)</th>
            <th>Condition (%)</th>
            <th>Hours Flown</th>
        </tr>`;
    if (data.length === 0) {
        html += `<tr><td colspan="7">No private sale aircraft available.</td></tr>`;
    } else {
        data.forEach(ac => {
            html += `<tr>
                <td>${ac.description}</td>
                <td>${ac.manufacturer}</td>
                <td>${ac.type}</td>
                <td>${ac.mtow}</td>
                <td>
                    ${ac.used_price}
                    <button class="market-btn buy-btn" data-id="${ac.id}" data-type="private">Buy</button>
                </td>
                <td>${ac.condition}</td>
                <td>${ac.hours_flown}</td>
            </tr>`;
        });
    }
    html += '</table>';
    document.getElementById('private-sale-list').innerHTML = html;
    attachMarketplaceButtonListeners(); // <-- Attach listeners here!
});
    } else if (section === 'ledger') {
        contentContainer.innerHTML = `
            <h2>Ledger</h2>
            <table id="ledger-table">
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>Date/Time</th>
                        <th>Pilot</th>
                        <th>Income (€)</th>
                        <th>Outgoing (€)</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Ledger rows will be populated by JavaScript -->
                </tbody>
            </table>
        `;
        loadLedger(); // Load ledger data
    }
}

// Function to load ledger data
function loadLedger() {
    fetch('/api/ledger')
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector('#ledger-table tbody');
            tbody.innerHTML = '';
            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.type}</td>
                    <td>${row.datetime}</td>
                    <td>${row.pilot}</td>
                    <td>${row.income ? '€' + row.income.toLocaleString() : ''}</td>
                    <td>${row.outgoing ? '-€' + Math.abs(row.outgoing).toLocaleString() : ''}</td>
                    <td>${row.description}</td>
                `;
                tbody.appendChild(tr);
            });
        });
}

// Call loadLedger() when the ledger page is loaded
if (window.location.pathname.endsWith('/ledger')) {
    document.addEventListener('DOMContentLoaded', loadLedger);
}

// Function to attach event listeners for the Operations section
function attachOperationsListeners() {
    const createPilotButton = document.getElementById("createPilotButton");
    if (createPilotButton) {
        createPilotButton.addEventListener("click", function () {
            console.log("Create Profile button clicked");
            const name = document.getElementById("pilotName")?.value.trim();
            const email = document.getElementById("pilotEmail")?.value.trim();
            const password = document.getElementById("pilotPassword")?.value.trim();

            if (!name || !email || !password) {
                alert("All fields are required!");
                return;
            }

            fetch("http://127.0.0.1:5000/api/create-pilot", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ name, email, password }),
            })
            .then(response => response.json())
            .then(data => {
                console.log("API response:", data);
                if (data.success) {
                    alert(`Pilot profile created successfully! Your Pilot ID is ${data.pilot_id}`);
                    // Optionally, clear the form or redirect
                    document.getElementById("createPilotForm").reset();
                } else {
                    // Handles duplicate email messages from backend
                    alert(data.message || "Failed to create pilot profile.");
                }
            })
            .catch(error => {
                console.error("Error creating pilot profile:", error);
                alert("Failed to create pilot profile. See console for details.");
            });
        });
    }

    const forgotPasswordLink = document.getElementById('forgot-password-link');
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', function(event) {
            event.preventDefault();
            const modal = document.getElementById('reset-password-modal');
            if (modal) {
                modal.style.display = 'block';
            }
        });
    }

    const resetPasswordBtn = document.getElementById('reset-password-btn');
    if (resetPasswordBtn) {
        resetPasswordBtn.addEventListener('click', function() {
            const email = document.getElementById('reset-email').value.trim();
            const newPassword = document.getElementById('reset-new-password').value.trim();

            if (!email || !newPassword) {
                alert('Please enter your email and new password.');
                return;
            }

            fetch('http://127.0.0.1:5000/api/reset-password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, new_password: newPassword })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.success) {
                    document.getElementById('reset-password-modal').style.display = 'none';
                }
            })
            .catch(() => alert('Error resetting password.'));
        });
    }
}


// After successful login:
function showPilotDashboard(pilot) {
    isLoggedIn = true; // Set login state
    const dashboard = document.getElementById('pilot-dashboard-profile');
    if (dashboard) {
        dashboard.innerHTML = `
            <div><strong>Pilot ID:</strong> <span id="dashboard-pilot-id">${pilot.identifier}</span></div>
            <div><strong>Name:</strong> <span id="dashboard-pilot-name">${pilot.name}</span></div>
            <div><strong>Rank:</strong> <span id="dashboard-pilot-rank">${pilot.rank}</span></div>
            <div><strong>Total Hours:</strong> <span id="dashboard-pilot-hours">${Number(pilot.total_hours).toFixed(1)}</span></div>
            <div><strong>Balance:</strong> <span id="dashboard-pilot-balance">${Number(pilot.balance).toFixed(0)}€</span></div>
            <div><strong>Location:</strong> <span id="dashboard-pilot-location">${pilot.current_location}</span></div>
            <div id="profile-dropdown">
                <button id="logout-btn">Log Out</button>
            </div>
        `;
        dashboard.style.display = 'block';
    } else {
        console.warn("Pilot dashboard element not found!");
    }

    // Show default message in content
    const contentContainer = document.getElementById('content-container');
    if (contentContainer) {
        contentContainer.innerHTML = '<p>Select an option from the menu to view content.</p>';
    }

    updateMenuVisibility(); // Update menu visibility based on login state

    // Store pilot info in localStorage
    localStorage.setItem('pilot', JSON.stringify(pilot));
    localStorage.setItem('isLoggedIn', 'true');

    // Fetch updated pilot data (e.g., balance) from the server
    fetch(`/api/pilot/${pilot.identifier}`)
      .then(res => res.json())
      .then(data => {
        // Update dashboard with data.balance
        const balanceSpan = document.getElementById('dashboard-pilot-balance');
        if (balanceSpan) balanceSpan.textContent = `${data.balance}€`;
      });
}


// Hide Job Market menu item if not logged in
function updateMenuVisibility() {
    const jobMarketLink = document.querySelector('a[onclick*="job-market"]');
    if (jobMarketLink) {
        jobMarketLink.style.display = isLoggedIn ? '' : 'none';
    }
}

// Call this after logout
function handleLogout() {
    isLoggedIn = false;
    // Hide profile banner
    const banner = document.getElementById('pilot-profile-banner');
    if (banner) {
        banner.style.display = 'none';
        banner.innerHTML = '';
    }
    // Hide dashboard/profile
    const dashboard = document.getElementById('pilot-dashboard-profile');
    if (dashboard) dashboard.style.display = 'none';
    // Reset main content to welcome page
    const contentContainer = document.getElementById('content-container');
    if (contentContainer) {
        contentContainer.innerHTML = '<p>Select an option from the menu to view content.</p>';
    }
    alert('You have been logged out.');
    updateMenuVisibility(); // Update menu visibility after logout
    // Optionally clear session/localStorage here if you're storing token etc.
    localStorage.removeItem('pilot');
    localStorage.removeItem('isLoggedIn');
}

// Attach logout handler (example)
document.addEventListener('click', function(event) {
    if (event.target && event.target.id === 'logout-btn') {
        handleLogout();
    }
});

// 🔹 MASTER EVENT LISTENER FOR CLICKS (Delegated for dynamically added elements)
document.addEventListener('click', function(event) {
    // Handle Log In button click
    if (event.target && event.target.id === "loginPilotButton") {
        console.log("Log In button clicked");

        const email = document.getElementById("loginEmail")?.value.trim();
        const password = document.getElementById("loginPassword")?.value.trim();

        if (!email || !password) {
            alert("Both fields are required!");
            return;
        }

        fetch("http://127.0.0.1:5000/api/login-pilot", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.pilot) {
                showPilotDashboard(data.pilot); // Show dashboard with pilot info
                alert("Login successful!");
            } else {
                alert(data.message || "Login failed.");
            }
        })
        .catch(error => {
            console.error("Error logging in:", error);
            alert("Failed to log in. See console for details.");
        });
    }

    // Toggle dropdown on profile banner or dashboard click
    const banner = document.getElementById('pilot-profile-banner');
    const dashboard = document.getElementById('pilot-dashboard-profile');
    const dropdown = document.getElementById('profile-dropdown');

    if ((banner && banner.contains(event.target) && event.target.id !== 'logout-btn') ||
        (dashboard && dashboard.contains(event.target) && event.target.id !== 'logout-btn')) {
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        }
    } else if (dropdown) {
        dropdown.style.display = 'none'; // Close dropdown if clicked outside
    }
});


// 🔹 FLIGHT LOG FORM SUBMISSION (Delegated)
document.addEventListener('submit', function(event) {
    if (event.target && event.target.id === 'flightLogForm') {
        event.preventDefault(); // Prevent default form submission

        const form = event.target;
        const data = {
            departure: form.departure.value,
            destination: form.destination.value,
            date: form.date.value,
            hours: parseFloat(form.hours.value),
            pilot_id: form.pilotId.value,
            aircraftType: form.aircraftType.value,
            aircraftIdent: form.aircraftIdent.value,
            flightNumber: form.flightNumber.value,
            takeoffsDay: parseInt(form.takeoffsDay.value),
            takeoffsNight: parseInt(form.takeoffsNight.value),
            landingsDay: parseInt(form.landingsDay.value),
            landingsNight: parseInt(form.landingsNight.value),
            instrumentApproach: parseInt(form.instrumentApproach.value)
        };

        // Get accepted job from localStorage
        let acceptedJob = JSON.parse(localStorage.getItem('acceptedJob') || 'null');

        // Check if flight matches accepted job and add reward if so
        if (
            acceptedJob &&
            data.departure === acceptedJob.departure_airport &&
            data.destination === acceptedJob.destination_airport &&
            data.flightNumber === acceptedJob.job_id
        ) {
            data.reward = acceptedJob.reward; // Add reward to payload
            alert(`Congratulations! You have been rewarded ${acceptedJob.reward}€ for completing job ${acceptedJob.job_id}.`);
            localStorage.removeItem('acceptedJob'); // Remove job after completion
        } else if (acceptedJob) {
            alert('Flight does not match the accepted job. No reward given.');
        }

        fetch('http://127.0.0.1:5000/api/submit-flight-log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                alert('Flight log submitted successfully!');
                form.reset();

                // Get the pilot object from localStorage
                let pilot = JSON.parse(localStorage.getItem('pilot') || '{}');

                // Update pilot fields if present in the response
                if (typeof result.balance !== "undefined") {
                    pilot.balance = result.balance;
                    const balanceSpan = document.getElementById('dashboard-pilot-balance');
                    if (balanceSpan) balanceSpan.textContent = `${pilot.balance}€`;
                }
                if (typeof result.rank !== "undefined") {
                    pilot.rank = result.rank;
                    const rankSpan = document.getElementById('dashboard-pilot-rank');
                    if (rankSpan) rankSpan.textContent = pilot.rank;
                }
                if (typeof result.total_hours !== "undefined") {
                    pilot.total_hours = result.total_hours;
                    const hoursSpan = document.getElementById('dashboard-pilot-hours');
                    if (hoursSpan) hoursSpan.textContent = pilot.total_hours;
                }
                if (typeof result.current_location !== "undefined") {
                    pilot.current_location = result.current_location;
                    const locationSpan = document.getElementById('dashboard-pilot-location');
                    if (locationSpan) locationSpan.textContent = pilot.current_location;
                }

                // Save updated pilot object to localStorage
                localStorage.setItem('pilot', JSON.stringify(pilot));

                // ...existing code for acceptedJob/jobRow...
            } else {
                alert('Failed to submit flight log: ' + (result.message || 'Unknown error.'));
            }
        })
        .catch(error => {
            console.error('Error submitting flight log:', error);
            alert('Error submitting flight log. Please check console for details.');
        });
    }
});

// 🔹 DOM CONTENT LOADED
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM fully loaded');

    // MENU EVENT LISTENERS (Handles submenu navigation)
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        const submenu = item.querySelector('.submenu');
        if (submenu) {
            const submenuLinks = submenu.querySelectorAll('a');
            submenuLinks.forEach(link => {
                link.addEventListener('click', function() {
                    console.log(`Submenu link clicked: ${this.textContent}`);
                    const parentMenuItem = this.closest('.menu-item');
                    if (parentMenuItem) {
                        const parentSubmenu = parentMenuItem.querySelector('.submenu');
                        if (parentSubmenu) {
                            parentSubmenu.style.display = 'none';
                        }
                    }
                });
            });
        }
    });

    // Check if user is already logged in (e.g., from session storage/local storage)
    // You would typically fetch user session from your backend on page load
    // For now, let's assume not logged in initially unless told otherwise.
    // In a real app, you'd make an AJAX call here to check login status.

    const pilotData = localStorage.getItem('pilot');
    const loggedIn = localStorage.getItem('isLoggedIn') === 'true';
    if (loggedIn && pilotData) {
        showPilotDashboard(JSON.parse(pilotData));
        isLoggedIn = true;
    }
    updateMenuVisibility(); // Hide or show menu items based on login status

    document.querySelectorAll('.buy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const aircraftId = this.getAttribute('data-id');
            const type = this.getAttribute('data-type');
            handleBuyAircraft(aircraftId, type);
        });
    });
    document.querySelectorAll('.lease-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const aircraftId = this.getAttribute('data-id');
            handleLeaseAircraft(aircraftId);
        });
    });
});

function handleBuyAircraft(aircraftId, type) {
    // Try both API routes for maximum compatibility
    let pilot = getCurrentPilot();
    let pilotId = pilot.identifier || window.currentPilotId;
    if (!pilotId) {
        alert('No pilot ID found. Please log in.');
        return;
    }
    // Prefer new route, fallback to old if needed
    fetch('/api/pilot/' + pilotId)
        .then(res => {
            if (!res.ok) return fetch('/api/get-pilot-profile?id=' + pilotId).then(r => r.json());
            return res.json();
        })
        .then(pilot => {
            if (!pilot || !pilot.identifier) {
                alert('Could not load pilot profile.');
                return;
            }
            fetch(`/api/aircraft/${aircraftId}`)
                .then(res => res.json())
                .then(ac => {
                    // Check rank unlock
                    if (!canPilotAccessAircraft(pilot.rank, ac.type)) {
                        alert('Your CPL rank is too low for this aircraft.');
                        return;
                    }
                    // Check balance
                    const price = type === 'private' ? ac.used_price : ac.cost_new;
                    if (pilot.balance < price) {
                        alert('Insufficient balance.');
                        return;
                    }
                    // Proceed with purchase
                    fetch('/api/marketplace/buy', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ pilot_id: pilot.identifier, aircraft_id: aircraftId, price, type })
                    })
                    .then(res => res.json())
                    .then(result => {
                        if (result.success) {
                            alert('Aircraft purchased!');
                            // Optionally refresh tables
                            updatePilotBalance(pilot.balance - price);
                            loadContent('fleet');
                        } else {
                            alert(result.message || 'Purchase failed.');
                        }
                    });
                });
        });
}

function handleLeaseAircraft(aircraftId) {
    // Similar logic as handleBuyAircraft, but for leasing
}

function canPilotAccessAircraft(rank, aircraftType) {
    // Map aircraft types to required ranks
    const smallTypes = ['Cessna', 'Piper'];
    const regionalTypes = ['CRJ', 'Citation'];
    const airlinerTypes = ['A320', '747'];

    if (smallTypes.some(t => aircraftType.includes(t))) {
        return ['CPL 1','CPL 2','CPL 3','CPL 4'].includes(rank);
    }
    if (regionalTypes.some(t => aircraftType.includes(t))) {
        return ['CPL 5','CPL 6','CPL 7','CPL 8'].includes(rank);
    }
    if (airlinerTypes.some(t => aircraftType.includes(t))) {
        return ['CPL 9','CPL 10','CPL 11','CPL 12'].includes(rank);
    }
    return false;
}

// Utility: Get pilot from localStorage
function getCurrentPilot() {
    return JSON.parse(localStorage.getItem('pilot') || '{}');
}

// Utility: Update pilot in localStorage and dashboard
function updatePilotBalance(newBalance) {
    let pilot = getCurrentPilot();
    pilot.balance = newBalance;
    localStorage.setItem('pilot', JSON.stringify(pilot));
    const balanceSpan = document.getElementById('dashboard-pilot-balance');
    if (balanceSpan) balanceSpan.textContent = `${Number(newBalance).toFixed(0)}€`;
}

// Utility: Check rank for MTOW (same as backend)
function canPilotAccessAircraftByMtow(rank, aircraftMtow) {
    // This mapping should be identical to the one in your app.py file
    const mtowLimits = {
        "CPL 1": 1500,
        "CPL 2": 2500,
        "CPL 3": 3500,
        "CPL 4": 5700,
        "CPL 5": 8000,
        "CPL 6": 12000,
        "CPL 7": 18000,
        "CPL 8": 25000,
        "CPL 9": 35000,
        "CPL 10": 50000,
        "CPL 11": 70000,
        "CPL 12": 100000,
    };

    const allowedMtow = mtowLimits[rank] || 0;
    
    return aircraftMtow <= allowedMtow;
}

// Attach after rendering Aircraft New table
function attachMarketplaceButtonListeners() {
    document.querySelectorAll('.buy-btn').forEach(btn => {
        btn.onclick = function() {
            const aircraftId = this.getAttribute('data-id');
            const type = this.getAttribute('data-type');
            handleBuyOrLeaseAircraft(aircraftId, type, 'buy');
        };
    });
    document.querySelectorAll('.lease-btn').forEach(btn => {
        btn.onclick = function() {
            const aircraftId = this.getAttribute('data-id');
            handleBuyOrLeaseAircraft(aircraftId, 'new', 'lease');
        };
    });
}

// Main handler for Buy/Lease
function handleBuyOrLeaseAircraft(aircraftId, type, action) {
    const pilot = getCurrentPilot();
    if (!pilot || !pilot.identifier) {
        alert('You must be logged in to buy or lease aircraft.');
        return;
    }
    fetch(`/api/aircraft/${aircraftId}`)
        .then(res => res.json())
        .then(ac => {
            // Use MTOW-based rank check
            if (!canPilotAccessAircraftByMtow(pilot.rank, ac.mtow)) {
                alert('Your CPL rank is too low for this aircraft.');
                return;
            }
            // Determine price
            let price = 0;
            if (action === 'buy') {
                if (type === 'private') {
                    // Calculate used_price based on condition (simulate same as backend)
                    const condition = ac.condition || Math.floor(Math.random() * 40) + 60; // fallback if not present
                    price = Math.round(ac.cost_new * (condition / 100));
                } else {
                    price = ac.cost_new;
                }
            } else if (action === 'lease') {
                price = ac.lease_price;
            }
            if (pilot.balance < price) {
                alert('Insufficient balance.');
                return;
            }
            // Proceed with buy/lease
            let body = {
                pilot_id: pilot.identifier,
                aircraft_id: aircraftId,
                price: price,
                type: type
            };
            if (action === 'lease') {
                body.lease_price = price; // Send lease_price for lease
            }
            fetch(`/api/marketplace/${action}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            })
            .then(res => res.json())
            .then(result => {
                if (result.success) {
                    alert(`Aircraft ${action === 'buy' ? 'purchased' : 'leased'}!`);
                    updatePilotBalance(pilot.balance - price);
                    loadContent('fleet'); // Move to Fleet tab
                } else {
                    alert(result.message || 'Transaction failed.');
                }
            });
        });
}

function showSellButton(aircraftIdent) {
    // Render a Sell button somewhere in the UI
    const sellBtn = document.createElement('button');
    sellBtn.textContent = 'Sell';
    sellBtn.onclick = function() {
        const pilot = getCurrentPilot();
        fetch('/api/fleet/sell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ aircraft_ident: aircraftIdent, pilot_id: pilot.identifier })
        })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                alert(`Aircraft sold for ${result.sale_price}€`);
                updatePilotBalance(pilot.balance + result.sale_price);
                loadContent('fleet');
            } else {
                alert(result.message || 'Sale failed.');
            }
        });
    };
    // Add sellBtn to the DOM (e.g., in a modal or below the row)
    document.body.appendChild(sellBtn); // Replace with your preferred placement
}

// Add repair button logic in the fleet section
document.addEventListener('DOMContentLoaded', function() {
    // Assuming fleet section is already loaded
    document.querySelectorAll('.repair-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const ident = this.getAttribute('data-ident');
            // Call repair API or function
            fetch('/api/fleet/repair', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ aircraft_ident: ident })
            })
            .then(res => res.json())
            .then(result => {
                if (result.success) {
                    alert('Aircraft repaired successfully!');
                    loadContent('fleet'); // Refresh fleet content
                } else {
                    alert('Repair failed: ' + (result.message || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Error repairing aircraft: ' + error.message);
            });
        });
    });
});

// Function to update the pilot's dashboard stats on the page
function updatePilotDashboard(pilotData) {
    if (pilotData) {
        document.getElementById('dashboard-pilot-id').textContent = `ID: ${pilotData.identifier}`;
        document.getElementById('dashboard-pilot-name').textContent = `Name: ${pilotData.pilot_name}`;
        document.getElementById('dashboard-pilot-rank').textContent = `Rank: ${pilotData.rank}`;
        document.getElementById('dashboard-pilot-hours').textContent = `Hours: ${pilotData.total_hours.toFixed(1)}`;
        document.getElementById('dashboard-pilot-balance').textContent = `Balance: ${pilotData.balance.toFixed(2)}€`;
        document.getElementById('dashboard-pilot-location').textContent = `Location: ${pilotData.current_location}`;
    }
}

// This event listener will handle the flight log form submission
document.addEventListener('DOMContentLoaded', () => {
    // We listen for the form submission on the entire document body
    // because the form is dynamically added and removed.
    document.body.addEventListener('submit', (e) => {
        // Check if the form being submitted is our flight log form
        if (e.target && e.target.id === 'flightLogForm') {
            e.preventDefault(); // Prevent the default form submission (page reload)

            const form = e.target;
            const formData = new FormData(form);

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('Flight log submitted and pilot stats updated successfully!');
                    
                    // Now, fetch the updated pilot data from the server
                    const pilot = JSON.parse(localStorage.getItem('pilot'));
                    if (pilot) {
                        fetch(`/api/pilot/${pilot.identifier}`)
                            .then(res => res.json())
                            .then(updatedPilotData => {
                                // Store the updated data in localStorage
                                localStorage.setItem('pilot', JSON.stringify(updatedPilotData));
                                
                                // Update the dashboard on the page
                                updatePilotDashboard(updatedPilotData);
                                
                                // Clean up accepted job data
                                localStorage.removeItem('acceptedJob');
                            })
                            .catch(error => {
                                console.error('Error fetching updated pilot data:', error);
                                alert('Flight logged, but failed to update pilot dashboard. Please refresh the page.');
                            });
                    }
                    
                } else {
                    alert('Error submitting flight log: ' + result.message);
                }
            })
            .catch(error => {
                console.error('Network or server error:', error);
                alert('An error occurred. Check the console for more details.');
            });
        }
    });
});