// Translation dictionary
const translations = {
    en: {
        candyCart: "Candy Cart",
        item: "Item",
        quantity: "Quantity",
        unit: "Unit",
        total: "Total",
        rewardPoints: "Reward Points",
        subtotal: "Subtotal:",
        gst: "GST:",
        qst: "QST:",
        total_amount: "Total:",
        callAssistance: "Call for Assistance",
        clearCart: "Clear Cart",
        searchItemCode: "Search Item Code",
        changeLanguage: "Change Language",
        payWithCard: "Pay with Card",
        searchItemByCode: "Search Item by Code",
        enterItemCode: "Enter item code",
        search: "Search",
        add: "Add",
        close: "Close",
        simulatePayment: "Simulate a Payment",
        scanOrEnterCard: "Please \"scan\" or enter a card number to simulate payment.",
        cardNumber: "Card Number",
        expiry: "Expiry (MM/YY)",
        pay: "Pay",
        cancel: "Cancel",
        youHavePoints: "You have ",
        wouldYouLikeRedeem: "Would you like to redeem $",
        yes: "Yes",
        no: "No",
        scanMembership: "Scan Membership Card",
        cannotScan: "Can't scan your card? No problem! Insert your number below.",
        submit: "Submit",
        continueWithout: "Continue without membership",
        paymentCompleted: "Payment completed!",
        receiptSent: "A receipt has been sent to the email associated with your account.",
        dontForgetCandy: "Don't forget your candy!"
    },

    fr: {
        candyCart: "Panier de Bonbons",
        item: "Article",
        quantity: "Quantité",
        unit: "Unité",
        total: "Total",
        rewardPoints: "Points Récompenses",
        subtotal: "Sous-total :",
        gst: "TPS :",
        qst: "TVQ :",
        total_amount: "Total :",
        callAssistance: "Appeler de l’aide",
        clearCart: "Vider le Panier",
        searchItemCode: "Rechercher un Code d’Article",
        changeLanguage: "Changer la Langue",
        payWithCard: "Payer par Carte",
        searchItemByCode: "Rechercher un article par code",
        enterItemCode: "Entrer le code de l’article",
        search: "Rechercher",
        add: "Ajouter",
        close: "Fermer",
        simulatePayment: "Simuler un Paiement",
        scanOrEnterCard: "Veuillez « scanner » ou entrer un numéro de carte.",
        cardNumber: "Numéro de Carte",
        expiry: "Expiration (MM/AA)",
        pay: "Payer",
        cancel: "Annuler",
        youHavePoints: "Vous avez ",
        wouldYouLikeRedeem: "Souhaitez-vous utiliser $",
        yes: "Oui",
        no: "Non",
        scanMembership: "Scanner la Carte de Membre",
        cannotScan: "Impossible de scanner? Entrez votre numéro.",
        submit: "Soumettre",
        continueWithout: "Continuer sans adhésion",
        paymentCompleted: "Paiement réussi!",
        receiptSent: "Un reçu a été envoyé à votre courriel.",
        dontForgetCandy: "N'oubliez pas vos bonbons!"
    }
};

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

window.onclick = (event) => {
    if (event.target === membershipModal) {
        membershipModal.style.display = "none";
        input.disabled = false;
        input.focus();
    }
};

function submitMembership() {
    updateCartDisplay();
    const membershipNumber = document.getElementById("membershipInput").value;
    console.log("Membership number submitted:", membershipNumber);
    membershipModal.style.display = "none";
    input.disabled = false;
    input.focus();

    fetch('/submit-membership', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ membershipNumber })
    })
    .then(response => response.json())
    .then(data => {
    console.log("Server response:", data);
    fetch('/get-reward-points', {
        method: 'GET'
    })
    .then(res => res.json())
    .then(pointsData => {
        if (pointsData.status === "success") {
            const points = pointsData.points;
            const discount = Math.floor(points / 100);
            if (discount > 0) {
                console.log('Membership detected... proceeding to points...')
                showPointsModal(points, discount);
            } else {
                console.log('No discount... proceeding to payment...');
                continueToPayment();
            }
        } else {
            console.log(pointsData);
            console.log('No membership... proceeding to payment...');
            continueToPayment();
        }
    });
    })
    .catch(error => {
        console.error("Error:", error);
        // still continue to payment if server not reachable
        continueToPayment();
    });
}

function showPointsModal(points, discount) {
    document.getElementById("pointsValue").textContent = points;
    document.getElementById("discountValue").textContent = discount;
    document.getElementById("pointsModal").style.display = "block";
}

function applyPointsDiscount() {
    fetch('/set-use-points', {
        method: 'POST'
    })
    .then(res => res.json())
    .then(pointsData => {
        if (pointsData.status === "success") {
            sessionStorage.setItem("usePoints", "true");
            document.getElementById("pointsModal").style.display = "none";
            continueToPayment();
        } else {
            document.getElementById("pointsModal").style.display = "none";
            continueToPayment();
        }
    });
}

function skipPointsDiscount() {
    sessionStorage.setItem("usePoints", "false");
    document.getElementById("pointsModal").style.display = "none";
    continueToPayment();
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
            paymentModal.style.display = "block";
            membershipModal.style.display = "block";
            input.disabled = true;
            input.blur();
            console.log(input.offsetParent !== null);
            document.getElementById("membershipInput").focus();
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
            showNotification("Cart item added successfully!", 3000);
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
        showNotification("Cart item(s) removed successfully!", 3000);
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
          showNotification("Cart item(s) removed successfully!", 3000);
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
            showPaymentConfirmation();
        } else {
            alert('Payment failed: ' + (data.message || 'Unknown'));
        }
    })
    .catch(err => {
        console.error('Payment error', err);
        alert('Payment request failed');
    });
}

function showPaymentConfirmation() {
    const modal = document.getElementById('payment-modal');
    modal.style.display = 'block';

    // Auto-close after 3 seconds (3000 milliseconds)
    setTimeout(() => {
        closeModal();
    }, 3000);
}

function closeModal() {
    document.getElementById('payment-modal').style.display = 'none';
}

function showNotification(message, duration = 3000) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, duration);
}

function callForAssistance() {
    console.log("Calling for assistance...");
}

function clearCart() {
    fetch('/clear-cart', {})
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateCartDisplay();
            calculateSummary();
        } else {
            alert(':Cart clearing failed. ' + (data.message || 'Unknown'));
        }
    })
    .catch(err => {
            console.error('Cart clearing error', err);
            alert('Cart clearing request failed');
    });
}

let currentItem = null;

function openSearchModal() {
    console.log('Opening search modal...')
    document.getElementById("searchModal").style.display = "block";
    document.getElementById("searchCodeInput").focus();
    document.getElementById("searchResult").innerHTML = "";
    document.getElementById("addItemBtn").style.display = "none";
    currentItem = null;
}

function closeSearchModal() {
    document.getElementById("searchModal").style.display = "none";
}

function searchItem() {
    console.log('Searching for item...')
    const code = document.getElementById("searchCodeInput").value;
    fetch('/search-item', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    })
    .then(res => {
        if (!res.ok) throw new Error("Item not found");
        return res.json();
    })
    .then(data => {
        currentItem = data.item;
        document.getElementById("searchResult").innerHTML = `
        <p><strong>Added ${data.item.name}</strong></p>
        `;
        updateCartDisplay();
        calculateSummary();
        showNotification("Cart item added successfully!", 3000);
    })
    .catch(err => {
        document.getElementById("searchResult").innerHTML = `<p style="color:red;">${err.message}</p>`;
        document.getElementById("addItemBtn").style.display = "none";
        currentItem = null;
    });
}

function addItem() {
    if (!currentItem) return;
    // Add to cart logic here
    console.log("Added to cart:", currentItem);
    closeSearchModal();
}

function changeLanguage(lang) {
    document.querySelectorAll("[data-translate]").forEach(el => {
        const key = el.getAttribute("data-translate");
        if (translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });

     // Update all placeholder translations
    document.querySelectorAll("[data-translate-placeholder]").forEach(el => {
        const key = el.getAttribute("data-translate-placeholder");
        if (translations[lang] && translations[lang][key]) {
            el.placeholder = translations[lang][key];
        }
    });
    
    localStorage.setItem("language", lang);
}

function toggleLanguage() {
    const current = localStorage.getItem("language") || "en";
    const next = current === "en" ? "fr" : "en";
    changeLanguage(next);
}

document.addEventListener("DOMContentLoaded", () => {
    const saved = localStorage.getItem("language") || "en";
    changeLanguage(saved);
});