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
        // After membership is accepted, continue to payment
        continueToPayment();
    })
    .catch(error => {
        console.error("Error:", error);
        // still continue to payment if server not reachable
        continueToPayment();
    });
}

function continueToPayment() {
    membershipModal.style.display = 'none';
    // Show payment modal so user can enter/scan card
    paymentModal.style.display = 'block';
    // focus card input for easy scanning
    const cardInput = document.getElementById('cardNumberInput');
    if (cardInput) cardInput.focus();
}

function closePaymentModal() {
    paymentModal.style.display = 'none';
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
        tbody.innerHTML = '';

        data.items.forEach(item => {
            const row = document.createElement('tr');
            row.setAttribute('data-id', item.id);
            row.innerHTML = `
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>$${item.unit.toFixed(2)}</td>
            <td>$${item.total.toFixed(2)}</td>
            <td class="remove-td">
                <button class="remove-btn">x</button>
            </td>
            `;
            tbody.appendChild(row);
        });

        calculateSummary(0.05, 0.09975);
        attachRemoveListeners();
    });
}

document.querySelectorAll('.remove-btn').forEach(button => {
  button.addEventListener('click', function () {
    console.log('Removing...')
    const itemRow = this.closest('tr');
    const itemId = itemRow.getAttribute('data-id');

    fetch('/remove-item', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: itemId })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        updateCartDisplay();
      } else {
        alert('Failed to remove item');
      }
    });
  });
});

function attachRemoveListeners() {
  document.querySelectorAll('.remove-btn').forEach(button => {
    button.addEventListener('click', function () {
      const itemRow = this.closest('tr');
      const itemId = itemRow.getAttribute('data-id');

      fetch('/remove-item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: itemId })
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          updateCartDisplay();
        } else {
          alert('Failed to remove item');
        }
      });
    });
  });
}

// Payment submit: collect card info and POST to server
function makePayment() {
        const cardNumber = document.getElementById('cardNumberInput').value;
        const expiry = document.getElementById('expiryInput').value;

        fetch('/finalize-payment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cardNumber, expiryDate: expiry })
        })
        .then(response => response.json())
        .then(data => {
                if (data.status === 'success') {
                        console.log('Payment processed:', data.message || data);
                        closePaymentModal();
                        updateCartDisplay();
                } else {
                        alert('Payment failed: ' + (data.message || 'Unknown'));
                }
        })
        .catch(err => {
                console.error('Payment error', err);
                alert('Payment request failed');
        });
}

// calculateSummary(0.05, 0.09975);