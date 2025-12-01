
// function renderCarts(carts) {
//     const container = document.getElementById('carts-list');
//     container.innerHTML = '';
//     if (!carts || carts.length === 0) {
//         container.innerHTML = '<p>No carts found for your account.</p>';
//         return;
//     }

//     carts.forEach(cart => {
//         const card = document.createElement('div');
//         card.className = 'cart-card';
//         const header = document.createElement('div');
//         header.className = 'cart-header';
//         header.innerHTML = `<strong>Cart #${cart.cartId}</strong> — Total: $${cart.totalCartPrice.toFixed(2)} — Points: ${cart.totalRewardPoints} — ${cart.checkoutDate}`;

//         const itemsTable = document.createElement('table');
//         itemsTable.className = 'cart-items';
//         itemsTable.innerHTML = `
//             <thead><tr><th>Product</th><th>Quantity</th><th>Total</th></tr></thead>
//             <tbody></tbody>
//         `;
//         const tbody = itemsTable.querySelector('tbody');
//         if (cart.items && cart.items.length) {
//             cart.items.forEach(i => {
//                 const r = document.createElement('tr');
//                 r.innerHTML = `<td>${i.productName || i.productId}</td><td>${i.quantity}</td><td>$${i.totalProductPrice.toFixed(2)}</td>`;
//                 tbody.appendChild(r);
//             });
//         } else {
//             const r = document.createElement('tr');
//             r.innerHTML = `<td colspan="3">No items recorded for this cart.</td>`;
//             tbody.appendChild(r);
//         }

//         card.appendChild(header);
//         card.appendChild(itemsTable);
//         container.appendChild(card);
//     });
// }

// function loadMyCarts() {
//     CartService.fetchMyCarts()
//     .then(resp => {
//         if (resp.status === 'success') {
//             renderCarts(resp.carts);
//         } else {
//             document.getElementById('carts-list').innerHTML = `<p class="error">${resp.message || 'Unable to load carts.'}</p>`;
//         }
//     })
//     .catch(err => {
//         document.getElementById('carts-list').innerHTML = `<p class="error">${err.message}</p>`;
//     });
// }

// document.addEventListener('DOMContentLoaded', () => {
//     loadMyCarts();
// });

// document.getElementById('logoutBtn').addEventListener('click', () => {
//     fetch('/logout', {
//         method: 'POST',
//         credentials: 'include'
//     })
//     .then(res => {
//         if (res.redirected) {
//             window.location.href = res.url;
//         } else {
//             window.location.reload(); // fallback
//         }
//     });
// });

// const modeToggle = document.getElementById('modeToggle');
// const htmlElement = document.documentElement;
// const body = document.body;

// // Check if user has a saved theme preference
// const savedMode = localStorage.getItem('darkMode');
// if (savedMode === 'true') {
//     body.classList.add('dark-mode');
//     updateToggleButton();
// }

// // Toggle dark mode on button click
// modeToggle.addEventListener('click', () => {
//     body.classList.toggle('dark-mode');
//     const isDarkMode = body.classList.contains('dark-mode');
//     localStorage.setItem('darkMode', isDarkMode);
//     updateToggleButton();
// });

// function updateToggleButton() {
//     const isDarkMode = body.classList.contains('dark-mode');
//     modeToggle.textContent = isDarkMode ? 'Light Mode' : 'Dark Mode';
// }

//---------------------------------------------------------
// 1. RENDER ALL RECEIPTS / CART HISTORY
//---------------------------------------------------------
function renderCarts(carts) {
    const container = document.getElementById('carts-list');
    container.innerHTML = '';

    if (!carts || carts.length === 0) {
        container.innerHTML = '<p>No carts found for your account.</p>';
        return;
    }

    carts.forEach(cart => {
        const card = document.createElement('div');
        card.className = 'cart-card';

        const header = document.createElement('div');
        header.className = 'cart-header';
        header.innerHTML = `
            <strong>Cart #${cart.cartId}</strong> — 
            Total: $${cart.totalCartPrice.toFixed(2)} — 
            Points: ${cart.totalRewardPoints} — 
            ${cart.checkoutDate}
        `;

        const itemsTable = document.createElement('table');
        itemsTable.className = 'cart-items';
        itemsTable.innerHTML = `
            <thead>
                <tr><th>Product</th><th>Quantity</th><th>Total</th></tr>
            </thead>
            <tbody></tbody>
        `;

        const tbody = itemsTable.querySelector('tbody');

        if (cart.items && cart.items.length) {
            cart.items.forEach(i => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${i.productName || i.productId}</td>
                    <td>${i.quantity}</td>
                    <td>$${i.totalProductPrice.toFixed(2)}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            const row = document.createElement('tr');
            row.innerHTML = `<td colspan="3">No items recorded for this cart.</td>`;
            tbody.appendChild(row);
        }

        card.appendChild(header);
        card.appendChild(itemsTable);
        container.appendChild(card);
    });
}

//---------------------------------------------------------
// 2. LOAD PURCHASE HISTORY FOR THE LOGGED-IN CUSTOMER
//---------------------------------------------------------
function loadMyCarts() {
    CartService.fetchMyCarts()
        .then(resp => {
            if (resp.status === 'success') {
                renderCarts(resp.carts);
                calculateTotalSpent(resp.carts);
            } else {
                document.getElementById('carts-list').innerHTML =
                    `<p class="error">${resp.message}</p>`;
            }
        })
        .catch(err => {
            document.getElementById('carts-list').innerHTML =
                `<p class="error">${err.message}</p>`;
        });
}

//---------------------------------------------------------
// 3. CALCULATE TOTAL SPENT DURING SELECTED PERIOD
//---------------------------------------------------------
function calculateTotalSpent(carts) {
    if (!carts) return;

    const total = carts.reduce((sum, cart) => sum + cart.totalCartPrice, 0);
    const totalBox = document.getElementById('total-spent');

    if (totalBox) {
        totalBox.textContent = `Total Spent: $${total.toFixed(2)}`;
    }
}

//---------------------------------------------------------
// 4. SEARCH PURCHASE HISTORY FOR A SPECIFIC ITEM
//---------------------------------------------------------
function searchItemHistory() {
    const query = document.getElementById('searchInput').value.trim().toLowerCase();
    const resultsBox = document.getElementById('search-results');

    if (!query) {
        resultsBox.innerHTML = '<p>Please enter an item name to search.</p>';
        return;
    }

    CartService.fetchMyCarts()
        .then(resp => {
            if (resp.status !== 'success') {
                resultsBox.innerHTML = '<p>Error loading purchase history.</p>';
                return;
            }

            const allCarts = resp.carts;
            let matches = [];

            allCarts.forEach(cart => {
                cart.items.forEach(item => {
                    if ((item.productName || "").toLowerCase().includes(query)) {
                        matches.push({
                            name: item.productName,
                            price: item.totalProductPrice,
                            date: cart.checkoutDate
                        });
                    }
                });
            });

            if (matches.length === 0) {
                resultsBox.innerHTML = `<p>No purchases found for "${query}".</p>`;
                return;
            }

            let html = `
                <p><strong>Item:</strong> ${matches[0].name}</p>
                <p><strong>Purchased:</strong> ${matches.length} times</p>
                <ul>
            `;

            matches.forEach(m => {
                html += `<li>${m.date} — $${m.price.toFixed(2)}</li>`;
            });

            html += `</ul>`;
            resultsBox.innerHTML = html;
        });
}

//---------------------------------------------------------
// 5. DOWNLOAD RECEIPTS AS PDF
//---------------------------------------------------------
function downloadPDF() {
    fetch('/download-receipts-pdf')
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'purchase_history.pdf';
            a.click();
        });
}

//---------------------------------------------------------
// 6. DOWNLOAD RECEIPTS AS CSV
//---------------------------------------------------------
function downloadCSV() {
    fetch('/download-receipts-csv')
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'purchase_history.csv';
            a.click();
        });
}

//---------------------------------------------------------
// 7. DARK MODE (YOUR ORIGINAL CODE)
//---------------------------------------------------------
const modeToggle = document.getElementById('modeToggle');
const body = document.body;

const savedMode = localStorage.getItem('darkMode');
if (savedMode === 'true') {
    body.classList.add('dark-mode');
    updateToggleButton();
}

modeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    const isDark = body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    updateToggleButton();
});

function updateToggleButton() {
    const isDark = body.classList.contains('dark-mode');
    modeToggle.textContent = isDark ? 'Light Mode' : 'Dark Mode';
}

//---------------------------------------------------------
// 8. LOGOUT
//---------------------------------------------------------
document.getElementById('logoutBtn').addEventListener('click', () => {
    fetch('/logout', { method: 'POST', credentials: 'include' })
        .then(res => {
            if (res.redirected) window.location.href = res.url;
            else window.location.reload();
        });
});

//---------------------------------------------------------
// 9. PAGE INITIALIZATION
//---------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    loadMyCarts();

    const searchBtn = document.getElementById('searchBtn');
    if (searchBtn) searchBtn.addEventListener('click', searchItemHistory);

    const pdfBtn = document.getElementById('downloadPdfBtn');
    if (pdfBtn) pdfBtn.addEventListener('click', downloadPDF);

    const csvBtn = document.getElementById('downloadCsvBtn');
    if (csvBtn) csvBtn.addEventListener('click', downloadCSV);
});
