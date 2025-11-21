// -------------------------
// TRANSLATIONS
// -------------------------
const translations = {
    en: {
        welcome: "Welcome",
        addCustomer: "Add Customer",
        customerName: "Customer Name",
        email: "Email",
        phone: "Phone Number",
        submit: "Submit",
        language: "Language",
        toggleLanguage: "Français"
    },
    fr: {
        welcome: "Bienvenue",
        addCustomer: "Ajouter un client",
        customerName: "Nom du client",
        email: "Courriel",
        phone: "Numéro de téléphone",
        submit: "Soumettre",
        language: "Langue",
        toggleLanguage: "English"
    }
};

// -------------------------
// CHANGE LANGUAGE FUNCTION
// -------------------------
function changeLanguage(lang) {
    // Save user preference
    localStorage.setItem("language", lang);

    // Update all elements with data-translate attributes
    document.querySelectorAll("[data-translate]").forEach(el => {
        const key = el.getAttribute("data-translate");

        if (translations[lang] && translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });

    // Update the toggle button label if exists
    const toggleBtn = document.getElementById("languageToggle");
    if (toggleBtn) {
        toggleBtn.textContent = translations[lang].toggleLanguage;
    }
}

// -------------------------
// LANGUAGE TOGGLE BUTTON
// -------------------------
document.addEventListener("DOMContentLoaded", () => {

    // Load saved language or default (English)
    const saved = localStorage.getItem("language") || "en";
    changeLanguage(saved);

    // If toggle button exists, connect event
    const toggleBtn = document.getElementById("languageToggle");

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            const current = localStorage.getItem("language") || "en";
            const newLang = current === "en" ? "fr" : "en";
            changeLanguage(newLang);
        });
    }
});
