function closeNotification() {
    const notification = document.getElementById("notification");
    if (notification) notification.style.display = "none";
}

function sendToggle(state) {
    fetch('/fan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: state })
    })
    .then(response => response.text())
    .then(data => console.log(data));
}

document.getElementById("productTableBody").addEventListener("click", (event) => {
    if (event.target.classList.contains("open-update-modal")) {
        const modal = document.querySelector(".update-modal");

        modal.style.display = "flex";
        setTimeout(() => modal.classList.add("active"), 10);

        modal.querySelectorAll("input").forEach(input => input.value = "");

        const row = event.target.closest("tr");
        if (row) {
            modal.querySelector('input[name="productId"]').value = row.cells[0].textContent.trim();
            modal.querySelector('input[name="name"]').value = row.cells[1].textContent.trim();
            modal.querySelector('input[name="type"]').value = row.cells[2].textContent.trim();
            modal.querySelector('input[name="price"]').value = row.cells[3].textContent.trim();
            modal.querySelector('input[name="expirationDate"]').value = row.cells[4].textContent.trim();
            modal.querySelector('input[name="manufacturerName"]').value = row.cells[5].textContent.trim();
            modal.querySelector('input[name="upc"]').value = row.cells[6].textContent.trim();
        }
    }
});

// Close modal when clicking Cancel
document.querySelector('.update-cancel-btn').addEventListener('click', () => {
    const modal = document.querySelector('.update-modal');
    modal.classList.remove('active'); 
    modal.addEventListener('transitionend', function handler() {
        modal.style.display = 'none';
        modal.removeEventListener('transitionend', handler); 
    });
});

document.querySelector('.update-modal').addEventListener('click', (event) => {
    if (event.target.classList.contains('update-modal')) {
        const modal = document.querySelector('.update-modal');
        modal.classList.remove('active'); 
        modal.addEventListener('transitionend', function handler() {
            modal.style.display = 'none';
            modal.removeEventListener('transitionend', handler);
        });
    }
});

// Open modal when clicking "+"
const addModalBtn = document.querySelector('.add-btn');

addModalBtn.addEventListener('click', () =>{
    const addModal = document.querySelector('.add-modal');

    addModal.querySelectorAll('input').forEach(input =>input.value = '');

    addModal.style.display= "flex";
    setTimeout(() =>{
        addModal.classList.add('active');
    }, 10);
});

// Close modal when clicking Cancel button
const add_cancelBtn = document.querySelector('.add-cancel-btn');

add_cancelBtn.addEventListener('click', () => {
    const addModal = document.querySelector('.add-modal');

    addModal.classList.remove('active');
    addModal.addEventListener('transitionend', function handler() {
        addModal.style.display = "none";
        addModal.removeEventListener('transitionend',handler);
    });
});

// Close modal when clicking outside of the modal
const clickOutside= document.querySelector('.add-modal');

clickOutside.addEventListener('click', (event) =>{
    if (event.target.classList.contains('add-modal'))
    {
        const addModal = document.querySelector('.add-modal');
        addModal.classList.remove('active');
        addModal.addEventListener('transitionend', function handler() {
            addModal.style.display = "none";
            addModal.removeEventListener('transitionend', handler);
        });
    }
});

const temperatureGauges = [];
const humidityGauges = [];

document.querySelectorAll("canvas[id^='temperature-gauge']").forEach((canvas, index) => {
    const gauge = new Gauge(canvas).setOptions({
        angle: 0,
        lineWidth: 0.3,
        radiusScale: 0.5,
        minValue: -10,
        maxValue: 40,
        animationSpeed: 32,
        staticZones: [
            {strokeStyle: "#F03E3E", min: -10, max: 3},
            {strokeStyle: "#30B32D", min: 3, max: 12},
            {strokeStyle: "#F03E3E", min: 12, max: 100}
        ]
    });
    gauge.setMinValue(-10);
    gauge.maxValue = 40;
    gauge.set(0);
    const key = canvas.id.replace("temperature-gauge-", "");
    temperatureGauges[key] = gauge;
});

document.querySelectorAll("canvas[id^='humidity-gauge']").forEach((canvas, index) => {
    const gauge = new Gauge(canvas).setOptions({
        angle: 0,
        lineWidth: 0.3,
        radiusScale: 0.5,
        minValue: 0,
        maxValue: 100,
        animationSpeed: 32,
        staticZones: [
            { strokeStyle: "#F03E3E", min: 0, max: 30 },    // too dry
            { strokeStyle: "#30B32D", min: 30, max: 60 },   // optimal
            { strokeStyle: "#FFDD00", min: 60, max: 80 },   // humid
            { strokeStyle: "#F03E3E", min: 80, max: 100 }   // too humid
        ]
    });
    gauge.setMinValue(0);
    gauge.maxValue = 100;
    gauge.set(50);
    const key = canvas.id.replace("humidity-gauge-", "");
    humidityGauges[key] = gauge;
});

async function updateReadings() {
    const response = await fetch("/sensor_data");
    const data = await response.json();

    Object.entries(data).forEach(([key, fridge]) => {
        // Update humidity text + meter
        const humidityText = document.getElementById(`humidity-${key}`);
        const humidityGauge = humidityGauges[key];

        if (humidityText) humidityText.textContent = fridge.humidity + "%";
        if (humidityGauge) humidityGauge.set(fridge.humidity);

        // Update temperature text + gauge
        const temperatureText = document.getElementById(`temperature-${key}`);
        const temperatureGauge = temperatureGauges[key];

        if (temperatureText) temperatureText.textContent = fridge.temperature + "°C";
        if (temperatureGauge) temperatureGauge.set(fridge.temperature);
    });
}

// Refresh every 5 seconds
setInterval(updateReadings, 5000);
updateReadings();

document.getElementById("addCustomerForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    try {
        const response = await fetch("/add", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error: " + response.status);
        }

        const result = await response.json();
        showNotification("Customer add successfully!");
        console.log(result);
    } catch (err) {
        console.error(err);
        showNotification("Error adding message: " + err.message);
    }
});

function showNotification(message, duration = 3000) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, duration);
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("updateProductForm").addEventListener("submit", async function(e) {
        console.log("submitting");
        e.preventDefault();
        const formData = new FormData(e.target);

        try {
            const response = await fetch("/update_product", {
                method: "POST",
                body: formData
            });

            if (!response.ok) throw new Error("Server error: " + response.status);

            const result = await response.json();
            console.log(result);
            showNotification("Product updated successfully!");

            document.querySelector(".update-modal").style.display = "none";
            refreshProducts();
        } catch (err) {
            showNotification("Product updated  un-successfully!");
            console.error(err);
        }
    });
});

async function refreshProducts() {
    try {
        const response = await fetch("/products");
        if (!response.ok) {
            showNotification("Failed to reload products. Try reloading your page.");
            return;
        }

        const products = await response.json();
        console.log(products)
        const tbody = document.getElementById("productTableBody");
        tbody.innerHTML = "";

        if (products.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" style="text-align:center;">No products found</td></tr>`;
        return;
        }

        products["products"].forEach((product, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${product.productId}</td>
                <td>${product.name}</td>
                <td>${product.type}</td>
                <td>${product.price}</td>
                <td>${product.expirationDate}</td>
                <td>${product.manufacturerName}</td>
                <td>${product.upc}</td>
                <td><button class="open-update-modal" data-index="${index+1}">Update</button></td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        showNotification("Failed to reload products. Try reloading your page.");
        console.error("Error refreshing products:", err);
    }
}