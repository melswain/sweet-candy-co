
function renderCarts(carts) {
    const container = document.getElementById("cart-results"); 
    container.innerHTML = ""; // only remove the carts

    carts.forEach(cart => {
        const card = `
            <div class="cart-card">
                <div class="cart-header">
                    <strong>Cart #${cart.cartId}</strong>
                    — Total: $${parseFloat(cart.totalCartPrice).toFixed(2)}
                    — ${cart.checkoutDate}
                </div>

                <table class="cart-items">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Total Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${cart.items.map(item => `
                            <tr>
                                <td>${item.productName}</td>
                                <td>${item.quantity}</td>
                                <td>$${parseFloat(item.totalProductPrice).toFixed(2)}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;

        container.insertAdjacentHTML("beforeend", card);
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


//when date had been inputted
const date_form = document.getElementById('date-filters');
const date_before_input = document.getElementById("date-before");
const date_after_input = document.getElementById("date-after");

    // //* Before Input
    date_before_input.addEventListener("change", async function(e){
        const formData = new FormData(date_form);

        try{
            const response = await fetch('/cart_history_filter', {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            
            if(response.ok && result.status === 'success'){
                console.log("Filter result received:", result);
                renderCarts(result.cart_history_data); 
            } else {
                const errorMessage = result.message || `Error fetching carts: ${response.statusText}`;
                document.getElementById('cart-results').innerHTML = `<p class="error">Error: ${errorMessage}</p>`;
                console.error(errorMessage.a);
            }
        }
        catch(err)
        {
            document.getElementById('cart-results').innerHTML = `<p class="error">Request Failed: ${err.message}</p>`;
            console.error("Filters request failed: ",err);
        }

    });

    // //* After Input
    date_after_input.addEventListener("change",async function(e){
        const formData = new FormData(date_form);
            try{
                const response = await fetch('/cart_history_filter', {
                    method: "POST",
                    body: formData
                });

                const result = await response.json();
                
                if(response.ok && result.status === 'success'){
                    console.log("Filter result received:", result);
                    // *** FIX: Render the newly fetched carts ***
                    renderCarts(result.cart_history_data);
                } else {
                    const errorMessage = result.message || `Error fetching carts: ${response.statusText}`;
                    document.getElementById('cart-results').innerHTML = `<p class="error">Error: ${errorMessage}</p>`;
                    console.error(errorMessage);
                }
            }
            catch(err)
            {
                document.getElementById('cart-results').innerHTML = `<p class="error">Request Failed: ${err.message}</p>`;
                console.error("Filters request failed: ",err);
            }
    });
