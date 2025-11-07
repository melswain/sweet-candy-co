function parseMoney(s) {
    return Number(String(s).replace(/[^0-9.-]+/g,"")) || 0;
}

function calculateSummary(gstRate,qstRate) {
    const rows = document.querySelectorAll('tbody tr');
    let subtotal = 0;

    rows.forEach(r => {
        const totalCell = r.cells[3];
        subtotal += parseMoney(totalCell.textContent);
    });

    const gst = Math.round((subtotal * gstRate) * 100) / 100;
    const qst = Math.round((subtotal * qstRate) * 100) / 100;
    const total = Math.round((subtotal + gst + qst) * 100) / 100;
    const rewardPoints = Math.floor(subtotal / 10) * 100;

    document.querySelector('.summary p:nth-child(1)').innerHTML = `<strong>Subtotal:</strong> $${subtotal.toFixed(2)}`;
    document.querySelector('.summary p:nth-child(2)').innerHTML = `<strong>GST:</strong> $${gst.toFixed(2)}`;
    document.querySelector('.summary p:nth-child(3)').innerHTML = `<strong>QST:</strong> $${qst.toFixed(2)}`;
    document.querySelector('.summary p:nth-child(4)').innerHTML = `<strong>Total:</strong> $${total.toFixed(2)}`;
    document.querySelector('.rewards-box p:nth-child(2)').textContent = rewardPoints;
}

const membershipModal = document.getElementById("membershipModal");
const closeBtn = document.querySelector(".close-button");
const paymentCloseBtn = document.querySelector(".pay-close-button");
const paymentModal = document.getElementById("paymentModal");
const input = document.getElementById('scanner-input');
input.focus();

document.getElementById("scanMembershipBtn").addEventListener("click", () => {
    membershipModal.style.display = "block";
});

closeBtn.onclick = () => {
    console.log('x');
    membershipModal.style.display = "none";
}

paymentCloseBtn.onclick = () => {
    console.log('x');
    paymentModal.style.display = "none";
}

window.onclick = (event) => {
    if (event.target === membershipModal) {
        membershipModal.style.display = "none";
    }
};

function submitMembership() {
    updateCartDisplay();
    const membershipNumber = document.getElementById("membershipInput").value;
    console.log("Membership number submitted:", membershipNumber);
    membershipModal.style.display = "none";

    fetch('/submit-membership', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ membershipNumber })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Server response:", data);
    })
    .catch(error => console.error("Error:", error));
}

function startPayment() {
    fetch('/get-membership')
    .then(response => response.json())
    .then(data => {
        if (data.membership_number) {
            console.log("Membership is set:", data.membership_number);
            paymentModal.style.display = "block";
        } else {
            console.log("No membership number found in session.");
            paymentModal.style.display = "block";
            membershipModal.style.display = "block";
        }
    });
}

function makePayment() {
    paymentModal.style.display = "none";
    fetch('/finalize-payment')
    .then(response => response.json())
    .then(data => {
        if (data.status) {
            console.log("Payment made:", data.status);
            updateCartDisplay();
        } else {
            console.log("Issues were encountered when trying to make a payment.");
        }
    });
}

let buffer = '';
let lastTime = 0;
const SCAN_TIMEOUT = 50;

window.addEventListener('keydown', (e) => {
    const now = Date.now();
    // ignore modifier keys
    if (e.key.length === 1) {
        if (now - lastTime > SCAN_TIMEOUT) buffer = ''; // new scan
        buffer += e.key;
        lastTime = now;
    } else if (e.key === 'Enter' && buffer.length) {
        scanCode(buffer);
        buffer = '';
    }
});

function scanCode(code) {
    console.log('Scanned code:', code);
    fetch('/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ code })
    })
    .then(r => r.json())
    .then(resp => {
        if (resp.status === "success") {
            updateCartDisplay();
        } else {
            alert('Scan error: ' + (resp.message || 'Unknown'));
        }
    })
    .catch(err => console.error(err));
}

function updateCartDisplay() {
    fetch('/cart-items')
    .then(response => response.json())
    .then(data => {
        const tbody = document.getElementById('cart-body');
        tbody.innerHTML = ''; // Clear existing rows

        data.items.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>$${item.unit.toFixed(2)}</td>
            <td>$${item.total.toFixed(2)}</td>
            `;
            tbody.appendChild(row);
        });
    });
}

// call once on load
// calculateSummary(0.05, 0.09975);