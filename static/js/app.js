const ageInput = document.querySelector("#age");
const incomeInput = document.querySelector("#income");
const scoreInput = document.querySelector("#score");
const pulseTitle = document.querySelector("#pulseTitle");
const pulseScore = document.querySelector("#pulseScore");
const pulseBar = document.querySelector("#pulseBar");
const pulseText = document.querySelector("#pulseText");

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

function getPersona(age, income, score) {
    const opportunity = Math.round(clamp((income / 120) * 45 + score * 0.55, 0, 100));

    if (score >= 72 && income >= 70) {
        return {
            title: "Premium opportunity",
            text: "High buying power and high interest. Personal offers or VIP-style campaigns can work well here.",
            opportunity,
        };
    }

    if (score >= 70 && age <= 32) {
        return {
            title: "Trend-driven explorer",
            text: "Young and highly active. Social campaigns, new arrivals and limited-time drops may attract this customer.",
            opportunity,
        };
    }

    if (income >= 75 && score < 45) {
        return {
            title: "Needs stronger engagement",
            text: "Income is promising, but spending intent is low. Try personalized recommendations or trust-building offers.",
            opportunity,
        };
    }

    if (score < 40) {
        return {
            title: "Value-focused visitor",
            text: "This customer may respond better to discounts, bundles and simple value-led messaging.",
            opportunity,
        };
    }

    return {
        title: "Balanced customer",
        text: "A steady profile. Loyalty points, combo deals and seasonal nudges can help increase repeat purchases.",
        opportunity,
    };
}

function updatePulsePreview() {
    const age = Number(ageInput?.value);
    const income = Number(incomeInput?.value);
    const score = Number(scoreInput?.value);

    if (!age || !income || !score) {
        pulseTitle.textContent = "Enter details to unlock a preview";
        pulseScore.textContent = "--";
        pulseBar.style.width = "8%";
        pulseText.textContent = "This preview updates before prediction, so the form feels more interactive and product-like.";
        return;
    }

    const persona = getPersona(age, income, score);
    pulseTitle.textContent = persona.title;
    pulseScore.textContent = `${persona.opportunity}%`;
    pulseBar.style.width = `${persona.opportunity}%`;
    pulseText.textContent = persona.text;
}

[ageInput, incomeInput, scoreInput].forEach((input) => {
    input?.addEventListener("input", updatePulsePreview);
});

updatePulsePreview();
