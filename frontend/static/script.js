document.addEventListener("DOMContentLoaded", function () {
    if (document.getElementById("registerBtn")) {
        document.getElementById("registerBtn").addEventListener("click", registerUser);
    }
    if (document.getElementById("loginBtn")) {
        document.getElementById("loginBtn").addEventListener("click", loginUser);
    }
    if (document.getElementById("uploadForm")) {
        document.getElementById("uploadForm").addEventListener("submit", uploadFile);
    }
    if (document.getElementById("myDocumentsBtn")) {
        document.getElementById("myDocumentsBtn").addEventListener("click", function () {
            showSection("myDocuments");
            fetchUserDocuments();
        });
    }
    if (localStorage.getItem("token")) {
        fetchUserProfile();
        fetchUserDocuments();
        fetchPendingRequests();
    }
});

// ✅ Show Loading Message
function showLoading(message) {
    const loadingDiv = document.createElement("div");
    loadingDiv.id = "loadingMessage";
    loadingDiv.textContent = message;
    loadingDiv.style.position = "fixed";
    loadingDiv.style.top = "10px";
    loadingDiv.style.left = "50%";
    loadingDiv.style.transform = "translateX(-50%)";
    loadingDiv.style.backgroundColor = "#000";
    loadingDiv.style.color = "#fff";
    loadingDiv.style.padding = "10px";
    loadingDiv.style.borderRadius = "5px";
    document.body.appendChild(loadingDiv);
}

// ✅ Hide Loading Message
function hideLoading() {
    const loadingDiv = document.getElementById("loadingMessage");
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

// ✅ User Registration
function registerUser() {
    let username = document.getElementById("registerUsername").value.trim();
    let password = document.getElementById("registerPassword").value.trim();

    if (!username || !password) {
        alert("Username and password cannot be empty.");
        return;
    }

    showLoading("Registering...");

    fetch("http://127.0.0.1:5000/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.message) {
            alert("Registration successful! Now log in.");
            window.location.href = "index.html"; 
        } else {
            alert("Registration failed: " + (data.error || "Unknown error"));
        }
    })
    .catch(error => {
        hideLoading();
        console.error("Register Fetch Error:", error);
        alert("Error: Could not connect to API.");
    });
}

// ✅ User Login
function loginUser() {
    let username = document.getElementById("loginUsername").value.trim();
    let password = document.getElementById("loginPassword").value.trim();

    if (!username || !password) {
        alert("Username and password cannot be empty.");
        return;
    }

    fetch("http://127.0.0.1:5000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.token) {
            localStorage.setItem("token", data.token);
            localStorage.setItem("userRole", data.role);
            
            if (data.role === "admin") {
                window.location.href = "admin_dashboard.html"; // ✅ Redirect Admins
            } else {
                window.location.href = "user_dashboard.html"; // ✅ Redirect Users
            }
        } else {
            alert("Login failed: " + (data.error || "Unknown error"));
        }
    })
    .catch(error => {
        console.error("Login Fetch Error:", error);
        alert("Error: Could not connect to API.");
    });
}


// ✅ Fetch User Profile
function fetchUserProfile() {
    let token = localStorage.getItem("token");

    if (!token) {
        console.error("🚨 No token found. User might be logged out.");
        alert("Session expired. Please log in again.");
        window.location.href = "index.html";
        return;
    }

    fetch("http://127.0.0.1:5000/user/profile", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        if (data.user) {
            document.getElementById("userName").textContent = data.user.username;
            document.getElementById("userRole").textContent = data.user.role;
            document.getElementById("userCredits").textContent = data.user.credits || "0";
            document.getElementById("totalRequests").textContent = data.user.total_requests || "0";  
        } else {
            alert("User profile not found.");
        }
    })
    .catch(error => {
        console.error("❌ Profile Fetch Error:", error);
    });
}





// ✅ Upload & Scan Document
function uploadFile(event) {
    event.preventDefault();

    let token = localStorage.getItem("token");
    let fileInput = document.getElementById("fileInput").files[0];

    if (!fileInput) {
        alert("Please upload a file!");
        return;
    }

    let formData = new FormData();
    formData.append("file", fileInput);

    showLoading("Uploading & scanning document...");

    fetch("http://127.0.0.1:5000/scan", {
        method: "POST",
        headers: { "Authorization": "Bearer " + token },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        let resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "<h3 class='font-semibold text-gray-800 mt-2'>Top Matches:</h3>";

        if (data.similar_documents && data.similar_documents.length > 0) {
            data.similar_documents.forEach(doc => {
                let docElement = document.createElement("p");
                docElement.textContent = `${doc.filename} - Similarity: ${doc.similarity}%`;
                resultsDiv.appendChild(docElement);
            });
        } else {
            resultsDiv.innerHTML += "<p class='text-gray-600'>No similar documents found.</p>";
        }

        fetchUserProfile();
        fetchUserDocuments();
    })
    .catch(error => {
        hideLoading();
        console.error("Upload Error:", error);
        alert("Error scanning document.");
    });
}

// ✅ Fetch My Documents

function fetchUserDocuments() {
    let token = localStorage.getItem("token");

    if (!token) {
        console.error("🚨 No token found. User might be logged out.");
        return;
    }

    fetch("http://127.0.0.1:5000/user/documents", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token} `}
    })
    .then(response => {
        console.log(`🔍 Fetch Documents Status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        console.log("✅ Documents Data:", data);
        if (!data.documents) {
            console.warn("⚠ No 'documents' key in response", data);
            return;
        }

        let docsDiv = document.getElementById("pastScans");
        if (!docsDiv) {
            console.error("❌ 'pastScans' element not found in HTML.");
            return;
        }

        let scansCount = document.getElementById("pastScansCount");
        docsDiv.innerHTML = "";

        if (data.documents.length === 0) {
            docsDiv.innerHTML = "<p class='text-gray-600'>No past scans available.</p>";
            if (scansCount) scansCount.textContent = "0";
            return;
        }

        if (scansCount) scansCount.textContent = data.documents.length;

        data.documents.forEach(doc => {
            let docElement = document.createElement("p");
            docElement.textContent = doc.filename;
            docsDiv.appendChild(docElement);
        });
    })
    .catch(error => {
        console.error("❌ Fetch Documents Error:", error);
    });
}

// ✅ User Requests Additional Credits
function requestCredits() {
    let token = localStorage.getItem("token");
    let requestedCredits = document.getElementById("creditRequestAmount").value.trim();

    if (!requestedCredits || requestedCredits <= 0) {
        alert("Please enter a valid credit amount.");
        return;
    }

    fetch("http://127.0.0.1:5000/user/request_credits", {
        method: "POST",
        headers: { "Authorization": "Bearer " + token, "Content-Type": "application/json" },
        body: JSON.stringify({ credits: parseInt(requestedCredits) })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || "Request submitted.");
        fetchUserProfile();
        fetchPendingRequests(); // ✅ Update pending requests immediately
    })
    .catch(error => {
        console.error("Credit Request Error:", error);
        alert("Error requesting credits.");
    });
}


// ✅ Fetch Pending Credit Requests (Admin)
function fetchCreditRequests() {
    let token = localStorage.getItem("token");

    fetch("http://127.0.0.1:5000/admin/credit_requests", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token} `}
    })
    .then(response => response.json())
    .then(data => {
        let requestsDiv = document.getElementById("creditRequests");
        requestsDiv.innerHTML = "";

        if (data.requests.length === 0) {
            requestsDiv.innerHTML = "<p>No pending credit requests.</p>";
            return;
        }

        data.requests.forEach(request => {
            let requestElement = document.createElement("div");
            requestElement.innerHTML = `
                <p><strong>${request.username}</strong> requested <strong>${request.credits}</strong> credits.</p>
                <button onclick="approveCredit(${request.id}, 'approve')">Approve</button>
                <button onclick="approveCredit(${request.id}, 'deny')">Deny</button>
                <hr>
            `;
            requestsDiv.appendChild(requestElement);
        });
    })
    .catch(error => {
        console.error("Fetch Credit Requests Error:", error);
    });
}


// ✅ Admin Approves/Deny Request
function approveCredit(requestId, decision) {
    let token = localStorage.getItem("token");

    fetch(`http://127.0.0.1:5000/admin/approve_credit/${requestId}`, {
        method: "POST",
        headers: { 
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ decision: decision })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchCreditRequests();
        fetchPendingRequests(); // ✅ Update user pending requests immediately
    })
    .catch(error => {
        console.error("Approve Credit Error:", error);
    });
}


// ✅ Fetch User Credit Status
function fetchCreditStatus() {
    let token = localStorage.getItem("token");

    if (!token) {
        console.error("🚨 No token found. User might be logged out.");
        return;
    }

    fetch("http://127.0.0.1:5000/user/credit_status", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        let statusText = `Requested: ${data.requested_credits} - Status: ${data.status}`;
        document.getElementById("pendingRequests").textContent = statusText;
    })
    .catch(error => {
        console.error("❌ Fetch Credit Status Error:", error);
    });
}

// ✅ Fetch credit status on page load
document.addEventListener("DOMContentLoaded", function () {
    fetchCreditStatus();
});

// ✅ Request Credits Function
function requestCredits() {
    let token = localStorage.getItem("token");
    let requestedCredits = document.getElementById("creditRequestAmount").value.trim();

    if (!requestedCredits || requestedCredits <= 0) {
        alert("Please enter a valid credit amount.");
        return;
    }

    fetch("http://127.0.0.1:5000/user/request_credits", {
        method: "POST",
        headers: { "Authorization": "Bearer " + token, "Content-Type": "application/json" },
        body: JSON.stringify({ credits: parseInt(requestedCredits) })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || "Request submitted.");
        fetchUserProfile();
    })
    .catch(error => {
        console.error("Credit Request Error:", error);
        alert("Error requesting credits.");
    });
}


// ✅ Fetch credit status on page load
document.addEventListener("DOMContentLoaded", function () {
    fetchCreditStatus();
});

function fetchPendingRequests() {
    let token = localStorage.getItem("token");

    if (!token) {
        console.error("🚨 No token found.");
        return;
    }

    fetch("http://127.0.0.1:5000/user/pending_requests", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        let pendingRequestsDiv = document.getElementById("pendingRequests");

        if (data.requests.length > 0) {
            pendingRequestsDiv.innerHTML = data.requests.map(req => 
                `<p>Requested ${req.credits} credits - Status: ${req.status}</p>`  // ✅ Fixed: Use backticks (`) instead of JSX-like syntax
            ).join(""); 
        } else {
            pendingRequestsDiv.innerHTML = "<p class='text-gray-600'>No pending requests.</p>";
        }
    })
    .catch(error => {
        console.error("❌ Fetch Pending Requests Error:", error);
    });
}

function fetchScansPerUser() {
    let token = localStorage.getItem("token");

    if (!token) {
        console.error("🚨 No token found.");
        return;
    }

    fetch("http://127.0.0.1:5000/admin/scans_per_user", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        let scanLogsTable = document.getElementById("scanLogs");

        if (!scanLogsTable) {  // ✅ Prevent error if element is missing
            console.error("❌ 'scanLogs' element not found in HTML.");
            return;
        }

        scanLogsTable.innerHTML = ""; // Clear old data

        if (!data.scans || data.scans.length === 0) {
            scanLogsTable.innerHTML = `
                <tr>
                    <td colspan="3" class="border border-gray-300 px-4 py-2 text-gray-600">No scan data available.</td>
                </tr>
            `;
            return;
        }

        data.scans.forEach(scan => {
            let row = document.createElement("tr");
            row.innerHTML = `
                <td class="border border-gray-300 px-4 py-2">${scan.username}</td>
                <td class="border border-gray-300 px-4 py-2">${scan.scan_date}</td>
                <td class="border border-gray-300 px-4 py-2">${scan.scan_count}</td>
            `;
            scanLogsTable.appendChild(row);
        });
    })
    .catch(error => {
        console.error("❌ Fetch Scan Logs Error:", error);
    });
}

// ✅ Fetch Most Common Scanned Document Topics
function fetchCommonTopics() {
    let token = localStorage.getItem("token");

    fetch("http://127.0.0.1:5000/admin/common_topics", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        let topicsList = document.getElementById("commonTopics");
        if (!topicsList) return;

        topicsList.innerHTML = "";

        if (!data.topics || data.topics.length === 0) {
            topicsList.innerHTML = "<li>No common topics found.</li>";
            return;
        }

        data.topics.forEach(topic => {
            let listItem = document.createElement("li");
            listItem.textContent = topic;
            topicsList.appendChild(listItem);
        });
    })
    .catch(error => {
        console.error("❌ Fetch Common Topics Error:", error);
    });
}

// ✅ Fetch topics when Analytics Section is opened
document.addEventListener("DOMContentLoaded", function () {
    fetchCommonTopics();
});



// Fetch scan logs when the analytics page is opened
document.addEventListener("DOMContentLoaded", function () {
    fetchScansPerUser();
});

// ✅ Fetch Top Users by Scans & Credit Usage
// ✅ Fetch Top Users by Scans & Credit Usage
function fetchTopUsers() {
    let token = localStorage.getItem("token");

    fetch("http://127.0.0.1:5000/admin/top_users", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        let topUsersTable = document.getElementById("topUsers");

        if (!topUsersTable) {
            console.error("❌ 'topUsers' element not found in HTML.");
            return;
        }

        topUsersTable.innerHTML = ""; // Clear old data

        if (!data.top_users || data.top_users.length === 0) {
            topUsersTable.innerHTML = `
                <tr>
                    <td colspan="3" class="border border-gray-300 px-4 py-2 text-gray-600">No user data available.</td>
                </tr>
            `;
            return;
        }

        data.top_users.forEach(user => {
            let row = document.createElement("tr");
            row.innerHTML = `
                <td class="border border-gray-300 px-4 py-2">${user.username}</td>
                <td class="border border-gray-300 px-4 py-2">${user.total_scans}</td>
                <td class="border border-gray-300 px-4 py-2">${user.credits}</td>
            `;
            topUsersTable.appendChild(row);
        });
    })
    .catch(error => {
        console.error("❌ Fetch Top Users Error:", error);
    });
}



// ✅ Fetch top users when User Management section is opened
document.addEventListener("DOMContentLoaded", function () {
    fetchTopUsers();
});

// ✅ Fetch Credit Usage Statistics
function fetchCreditUsageStats() {
    let token = localStorage.getItem("token");

    fetch("http://127.0.0.1:5000/admin/credit_usage_stats", {
        method: "GET",
        headers: { "Authorization": `Bearer ${token}` }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("pendingCredits").textContent = data.pending || 0;
        document.getElementById("approvedCredits").textContent = data.approved || 0;
        document.getElementById("deniedCredits").textContent = data.denied || 0;
    })
    .catch(error => {
        console.error("❌ Fetch Credit Usage Stats Error:", error);
    });
}



// ✅ Logout Function
function logout() {
    localStorage.clear();
    alert("You have been logged out.");
    window.location.href = "index.html";
}

// ✅ Fetch credit status on page load
document.addEventListener("DOMContentLoaded", function () {
    fetchPendingRequests();
});