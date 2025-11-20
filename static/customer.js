class CartService {
    static async fetchMyCarts() {
        const res = await fetch('/my-carts');
        if (!res.ok) throw new Error('Failed to fetch carts');
        return res.json();
    }
}

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

document.querySelectorAll('.open-update-modal').forEach((btn) => {
        btn.addEventListener('click', (event) => {
            const modal = document.querySelector('.update-modal');
            

            modal.style.display = 'flex'; 
            
            setTimeout(() => {
                modal.classList.add('active'); // Add 'active' class to trigger fade-in
            }, 10); // A small delay is usually sufficient

            modal.querySelectorAll('input').forEach(input => input.value = '');

            const row = event.target.closest('tr');
            if (row) {
                modal.querySelector('input[name="productId"]').value = row.cells[0].textContent.trim();
                modal.querySelector('input[name="name"]').value = row.cells[1].textContent.trim();
                modal.querySelector('input[name="type"]').value = row.cells[2].textContent.trim();
                modal.querySelector('input[name="price"]').value = row.cells[3].textContent.trim();
                modal.querySelector('input[name="expirationDate"]').value = row.cells[4].textContent.trim();
                modal.querySelector('input[name="manufacturerName"]').value = row.cells[5].textContent.trim();
                modal.querySelector('input[name="upc"]').value = row.cells[6].textContent.trim();
                modal.querySelector('input[name="epc"]').value = row.cells[7].textContent.trim();
                modal.querySelector('input[name="quantity"]').value = row.cells[8].textContent.trim();
            }
        });
    });