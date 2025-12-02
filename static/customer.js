// ----------------------------------------------CART-HISTORY----------------------------------------------------------------------
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

const modeToggle = document.getElementById('modeToggle');
const htmlElement = document.documentElement;
const body = document.body;

// Check if user has a saved theme preference
const savedMode = localStorage.getItem('darkMode');
if (savedMode === 'true') {
    body.classList.add('dark-mode');
    updateToggleButton();
}

// Toggle dark mode on button click
modeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    const isDarkMode = body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
    updateToggleButton();
});

function updateToggleButton() {
    const isDarkMode = body.classList.contains('dark-mode');
    modeToggle.textContent = isDarkMode ? 'Light Mode' : 'Dark Mode';
}

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

    date_form.addEventListener("submit", async function(e){
        e.preventDefault();
        const formData = new FormData(date_form);
        const download_format = document.getElementById("cart-history-format").value;
        console.log("downloading");
        try{
            const response = await fetch('/download_cart_history',{
                method: "POST",
                body: formData
            });

            if(!response.ok){
                const errorMessage = await response.json();
                document.getElementById('cart-results').innerHTML = `<p class="error">Error: ${errorMessage}</p>`;
                console.error(errorMessage.a);
            }
            else{
                 const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);

                    const a = document.createElement("a");
                    a.href = url;
                    a.download =  `cart_history.${download_format}`;
                    a.click();
                    window.URL.revokeObjectURL(url);
            }
        }
        catch(err)
        {
            document.innerHTML = `<p class="error">Request failed: ${err.message}</p>`;
            console.error("Cart History download failed:", err);
        }
    })

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

    // ------------------------ RENDER RECEIPTS ------------------------------
function renderReceipts(receipts) {
    const container = document.getElementById("receipt-results");
    container.innerHTML = "";

    receipts.forEach(receipt => {
        const card = `
            <div class="cart-card">
                <div class="cart-header">
                    <strong>Receipt #${receipt.receiptId}</strong>
                    — Total: $${parseFloat(receipt.totalAmount).toFixed(2)}
                    — ${receipt.purchaseDate}
                </div>

                <table class="cart-items">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Qty</th>
                            <th>Total Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${receipt.items.map(item => `
                            <tr>
                                <td>${item.productName}</td>
                                <td>${item.quantity}</td>
                                <td>$${parseFloat(item.totalPrice).toFixed(2)}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            </div>
        `;

        container.insertAdjacentHTML("beforeend", card);
    });
}


    // ------------------------------------------------------Product Search History-------------------------------------------------
    function renderPurchaseSearchResults(report, productName) {
    const outputEl = document.getElementById('search-results-output');
    outputEl.innerHTML = '';
    
    if (!report || report.details.length === 0) {
        outputEl.innerHTML = `<p class="history-tip">No purchase history found for "${productName}".</p>`;
        return;
    }

    const header = `
        <h3 style="font-weight: 700; margin-bottom: 10px; color: #d81b60;">Product: ${report.product_name}</h3>
        <p style="font-size: 1.1rem; margin-bottom: 15px;">
            Purchased: <strong style="color: #4CAF50;">${report.total_purchases_count}</strong> units in total.
        </p>
        <div style="font-weight: 600; padding: 5px 0; border-bottom: 2px solid #ccc; display: flex; justify-content: space-between;">
            <span style="width: 40%;">Date & Time</span>
            <span style="width: 20%; text-align: right;">Quantity</span>
            <span style="width: 40%; text-align: right;">Total Price (for quantity)</span>
        </div>
    `;
    
    let detailsHtml = '';
    report.details.forEach(detail => {
        detailsHtml += `
            <div class="purchase-detail-row">
                <span style="width: 40%;">${detail.checkoutDate}</span>
                <span style="width: 20%; text-align: right;">${detail.quantity}</span>
                <span style="width: 40%; text-align: right;">$${parseFloat(detail.totalProductPrice).toFixed(2)}</span>
            </div>
        `;
    });
    
    outputEl.innerHTML = header + detailsHtml;
}


const searchForm = document.getElementById('product-search-form');
const search_product_download = document.getElementById("search-product-download").value;

    searchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const productName = document.getElementById('product-name-input').value.trim();
        const outputEl = document.getElementById('search-results-output');
        const clickedButton = e.submitter.value;
        
        if (!productName) {
            outputEl.innerHTML = `<p class="error">Please enter a product name.</p>`;
            return;
        }
        if(clickedButton === "download"){
            try{
                const download_format = document.getElementById("search-product-download").value;
                const response = await fetch('/download_purchase_search',{
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:JSON.stringify({
                        product_name: productName,
                        format: download_format
                    })
                });

                if(!response.ok){
                    const error = await response.json();
                    outputEl.innerHTML = `<p class="error">${error.message}</p>`;
                    return;                
                }
                else{
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);

                    const a = document.createElement("a");
                    a.href = url;
                    a.download =  `purchase_search.${download_format}`;
                    a.click();

                    window.URL.revokeObjectURL(url);
                }
            }
            catch(err)
            {
            outputEl.innerHTML = `<p class="error">Request failed: ${err.message}</p>`;
            console.error("Product search download failed:", err);
            }
        }   
        else{
        
        outputEl.innerHTML = `<p style="text-align: center; padding: 20px;">Searching for "${productName}"...</p>`;

        try {
            const response = await fetch('/search_purchases', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ product_name: productName })
            });
            
            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                renderPurchaseSearchResults(result.report, productName);
            } else {
                outputEl.innerHTML = `<p class="error">Error: ${result.message || 'Failed to search purchase history.'}</p>`;
            }
        } 
        catch (err) {
            outputEl.innerHTML = `<p class="error">Request failed: ${err.message}</p>`;
            console.error("Product search failed:", err);
        }            
        }

    });

// -----------------------------------------------------Total Spending-----------------------------------------------------
function renderTotalSpendingReport(spendingReport){
    const container = document.getElementById("total-spending-amount");
    const spending_report = Number(spendingReport) || 0.0;
    container.innerText = `$${spending_report.toFixed(2)}`;
}

const spending_date_form = document.getElementById('spending-date-filters');
const spending_date_before_input = document.getElementById("spending-date-before");
const spending_date_after_input = document.getElementById("spending-date-after");

    //* (Spending) Before Input
        spending_date_before_input.addEventListener("change", async function(e){
        const formData = new FormData(spending_date_form);

        try{
            const response = await fetch('/total_spending_filters', {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            
            if(response.ok && result.status === 'success'){
                console.log("Filter result received:", result);
                renderTotalSpendingReport(result.spending_report); 
            } else {
                const errorMessage = result.message || `Error fetching spending report: ${response.statusText}`;
                document.getElementById('total-spending-amount').innerHTML = `<p class="error">Error: ${errorMessage}</p>`;
                console.error(errorMessage.a);
            }
        }
        catch(err)
        {
            document.getElementById('total-spending-amount').innerHTML = `<p class="error">Request Failed: ${err.message}</p>`;
            console.error("Filters request failed: ",err);
        }

    });

     //* (Spending) After Input
        spending_date_after_input.addEventListener("change", async function(e){
        const formData = new FormData(spending_date_form);

        try{
            const response = await fetch('/total_spending_filters', {
                method: "POST",
                body: formData
            });

            const result = await response.json();

            
            if(response.ok && result.status === 'success'){
                console.log("Filter result received:", result);
                renderTotalSpendingReport(result.spending_report); 
            } else {
                const errorMessage = result.message || `Error fetching spending report: ${response.statusText}`;
                document.getElementById('total-spending-amount').innerHTML = `<p class="error">Error: ${errorMessage}</p>`;
                console.error(errorMessage.a);
            }
        }
        catch(err)
        {
            document.getElementById('total-spending-amount').innerHTML = `<p class="error">Request Failed: ${err.message}</p>`;
            console.error("Filters request failed: ",err);
        }

    });
    spending_date_form.addEventListener("submit", async function(e){
        e.preventDefault();
        const formData = new FormData(spending_date_form);
        const download_format = document.getElementById('spending-report-download').value;
        try{
            const response = await fetch('/download_spending_report',{
                method:"POST",
                body:formData
            })
            if(!response.ok)
            {
                const errorMessage = await response.json();
                document.getElementById('total-spending-amount').innerHTML = `<p class="error">Error: ${errorMessage}</p>`;
                console.error(errorMessage.a);
            }
            else{
                const blob = await response.blob();
                 const url = window.URL.createObjectURL(blob);

                const a = document.createElement("a");
                a.href = url;
                a.download =  `spending_report.${download_format}`;
                a.click();
                window.URL.revokeObjectURL(url);
            }
        }
        catch(err){
             document.innerHTML = `<p class="error">Request failed: ${err.message}</p>`;
            console.error("Spending Report download failed:", err);
        }
    });

    // ---------------------- RECEIPT FILTERING ------------------------------
const receipt_form = document.getElementById("receipt-filters");
const receipt_before = document.getElementById("receipt-before");
const receipt_after = document.getElementById("receipt-after");

async function applyReceiptFilters() {
    const formData = new FormData(receipt_form);

    try {
        const response = await fetch("/receipt_history_filter", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (response.ok && result.status === "success") {
            renderReceipts(result.receipt_history_data);
        } else {
            document.getElementById("receipt-results").innerHTML =
                `<p class="error">${result.message || "Error loading receipts."}</p>`;
        }
    }
    catch (err) {
        document.getElementById("receipt-results").innerHTML =
            `<p class="error">Request Failed: ${err.message}</p>`;
    }
}

receipt_before.addEventListener("change", applyReceiptFilters);
receipt_after.addEventListener("change", applyReceiptFilters);

// ---------------------- RECEIPT DOWNLOAD -------------------------------
receipt_form.addEventListener("submit", async function (e) {
    e.preventDefault();
    const formData = new FormData(receipt_form);
    const download_format = document.getElementById("receipt-format").value;

    try {
        const response = await fetch("/download_receipt_history", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            document.getElementById("receipt-results").innerHTML =
                `<p class="error">${error.message}</p>`;
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = `receipt_history.${download_format}`;
        a.click();

        window.URL.revokeObjectURL(url);
    }
    catch (err) {
        document.getElementById("receipt-results").innerHTML =
            `<p class="error">Download failed: ${err.message}</p>`;
    }
});
