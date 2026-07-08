from flask import Flask, redirect, render_template, request, url_for
import joblib
import pandas as pd

app = Flask(__name__)

# Load the trained preprocessing and clustering models.
scaler = joblib.load("model/scaler.pkl")
kmeans = joblib.load("model/kmeans_model.pkl")


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/home")
def homepage():
    return render_template("home.html")


@app.route("/predict", methods=["POST"])
def predict():
    age = float(request.form["age"])
    income = float(request.form["income"])
    score = float(request.form["score"])

    user = pd.DataFrame(
        [[age, income, score]],
        columns=["Age", "Annual Income (k$)", "Spending Score (1-100)"],
    )
    user_scaled = scaler.transform(user)
    cluster = kmeans.predict(user_scaled)[0]

    labels = {
        0: "High Income - High Spending",
        1: "Value-Conscious Customer",
        2: "Young Trend Explorer",
        3: "Everyday Customer",
        4: "Premium Customer",
    }

    recommendations = {
        0: "Recommend luxury products, premium memberships and exclusive offers.",
        1: "Offer discounts, budget-friendly products and seasonal sales.",
        2: "Target with social media marketing, trendy products and student discounts.",
        3: "Promote regular offers, combo deals and loyalty programs.",
        4: "Provide VIP services, personalized shopping and premium collections.",
    }

    playbooks = {
        0: {
            "action": "Invite to an exclusive launch or premium membership plan.",
            "offer": "VIP bundle, early access, luxury add-on",
            "channel": "Personalized email + WhatsApp follow-up",
        },
        1: {
            "action": "Show value packs and limited-time discount campaigns.",
            "offer": "Coupons, cashback, budget combo",
            "channel": "SMS + homepage deal banner",
        },
        2: {
            "action": "Use trend-led creatives with social proof and urgency.",
            "offer": "New arrivals, student discount, flash sale",
            "channel": "Instagram/Reels + push notification",
        },
        3: {
            "action": "Nudge repeat purchase with simple loyalty rewards.",
            "offer": "Combo deal, points booster, seasonal offer",
            "channel": "Email newsletter + app notification",
        },
        4: {
            "action": "Treat as a high-value relationship, not a one-time sale.",
            "offer": "Personal shopper, premium collection, VIP support",
            "channel": "Direct email + relationship manager call",
        },
    }

    opportunity_score = round(min(max((income / 120) * 45 + score * 0.55, 0), 100))

    return render_template(
        "result.html",
        age=age,
        income=income,
        score=score,
        prediction=labels.get(cluster, "Unclassified Customer"),
        recommendation=recommendations.get(
            cluster, "Collect more customer data before choosing a campaign."
        ),
        playbook=playbooks.get(
            cluster,
            {
                "action": "Collect more customer data before choosing a campaign.",
                "offer": "Exploratory offer",
                "channel": "General marketing campaign",
            },
        ),
        opportunity_score=opportunity_score,
    )


@app.route("/result")
def result():
    # Results need prediction data, so a direct visit returns to the input form.
    return redirect(url_for("home"))


if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
