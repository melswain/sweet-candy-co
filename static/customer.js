
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
        header.innerHTML = `<strong>Cart #${cart.cartId}</strong> — Total: $${cart.totalCartPrice.toFixed(2)} — Points: ${cart.totalRewardPoints} — ${cart.checkoutDate}`;

        const itemsTable = document.createElement('table');
        itemsTable.className = 'cart-items';
        itemsTable.innerHTML = `
            <thead><tr><th>Product</th><th>Quantity</th><th>Total</th></tr></thead>
            <tbody></tbody>
        `;
        const tbody = itemsTable.querySelector('tbody');
        if (cart.items && cart.items.length) {
            cart.items.forEach(i => {
                const r = document.createElement('tr');
                r.innerHTML = `<td>${i.productName || i.productId}</td><td>${i.quantity}</td><td>$${i.totalProductPrice.toFixed(2)}</td>`;
                tbody.appendChild(r);
            });
        } else {
            const r = document.createElement('tr');
            r.innerHTML = `<td colspan="3">No items recorded for this cart.</td>`;
            tbody.appendChild(r);
        }

        card.appendChild(header);
        card.appendChild(itemsTable);
        container.appendChild(card);
    });
}

function loadMyCarts() {
    CartService.fetchMyCarts()
    .then(resp => {
        if (resp.status === 'success') {
            renderCarts(resp.carts);
        } else {
            document.getElementById('carts-list').innerHTML = `<p class="error">${resp.message || 'Unable to load carts.'}</p>`;
        }
    })
    .catch(err => {
        document.getElementById('carts-list').innerHTML = `<p class="error">${err.message}</p>`;
    });
}

// Auto-load when this script is included
document.addEventListener('DOMContentLoaded', () => {
    loadMyCarts();
});

document.getElementById('logoutBtn').addEventListener('click', () => {
    fetch('/logout', {
        method: 'POST',
        credentials: 'include'
    })
    .then(res => {
        if (res.redirected) {
            window.location.href = res.url;
        } else {
            window.location.reload(); // fallback
        }
    });
});
