from flask import Flask, redirect, render_template, request, url_for, flash, send_file
from reportlab.pdfgen import canvas
import joblib
import pandas as pd
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
from collections import Counter
import seaborn as sns

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "priyanshi_secret_key"

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
# Load the trained preprocessing and clustering models.
scaler = joblib.load("model/scaler.pkl")
kmeans = joblib.load("model/kmeans_model.pkl") 

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    age = db.Column(db.Float)
    income = db.Column(db.Float)
    score = db.Column(db.Float)
    segment = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Account Created Successfully! Please Login.", "success")

        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
               login_user(user)
               flash("Login Successful!", "success")
               return redirect(url_for("homepage"))

        flash("Invalid Email or Password", "danger")

    return render_template("login.html")

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/home")
@login_required
def homepage():
    return render_template("home.html")

@app.route("/dashboard")
@login_required
def dashboard():

    total_predictions = Prediction.query.filter_by(
        user_id=current_user.id
    ).count()

    predictions = Prediction.query.filter_by(
        user_id=current_user.id
    ).order_by(Prediction.id.desc()).all()

    # Pie Chart Data
    segments = [p.segment for p in predictions]
    count = Counter(segments)

    if segments:
        # Pie Chart
        plt.figure(figsize=(6, 6))
        plt.pie(
            list(count.values()),
            labels=list(count.keys()),
            autopct="%1.1f%%",
            startangle=90,
        )
        plt.title("Customer Distribution")
        plt.tight_layout()
        plt.savefig("static/images/pie_chart.png", dpi=300)
        plt.close()

        # Bar Chart
        plt.figure(figsize=(8, 5))
        colors = ["#0b5d3b", "#1e88e5", "#ff9800", "#9c27b0", "#e91e63"]
        keys = list(count.keys())
        values = list(count.values())
        plt.bar(
    count.keys(),
    count.values(),
    color=["#4CAF50","#2196F3","#FF9800","#9C27B0","#E91E63"][:len(count)],
    edgecolor="black",
    linewidth=1.5
)
        plt.title("Customer Segments", fontsize=16)
        plt.xlabel("Segment")
        plt.ylabel("Number of Customers")
        plt.xticks(rotation=15)
        for i, value in enumerate(values):
            plt.text(i, value + 0.1, str(value), ha="center", fontsize=12)
        plt.tight_layout()
        plt.savefig("static/images/bar_chart.png", dpi=300)
        plt.close()

        # Bubble Chart
        df = pd.read_csv("dataset/Mall_Customers.csv")

        plt.figure(figsize=(8,6))

        sns.scatterplot(
            data=df,
            x="Annual Income (k$)",
            y="Spending Score (1-100)",
            hue="Spending Score (1-100)",
            size="Annual Income (k$)",
            palette="viridis",
            sizes=(40,300),
            alpha=0.8
        )

        plt.title("Customer Income vs Spending Score")
        plt.xlabel("Annual Income (k$)")
        plt.ylabel("Spending Score")

        plt.legend([], [], frameon=False)

        plt.tight_layout()
        plt.savefig("static/images/bubble_chart.png", dpi=300)
        plt.close()

    return render_template(
        "dashboard.html",
        total_predictions=total_predictions,
        predictions=predictions,
    )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/predict", methods=["POST"])
@login_required
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

    segment = {
      0: "High Income - High Spending",
      1: "Value-Conscious Customer",
      2: "Young Trend Explorer",
      3: "Everyday Customer",
      4: "Premium Customer",
    }.get(cluster, "Unknown")

    new_prediction = Prediction(
    user_id=current_user.id,
    age=age,
    income=income,
    score=score,
    segment=segment
)

    db.session.add(new_prediction)
    db.session.commit()
    


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

with app.app_context():
    db.create_all()
@app.route("/download-report")
@login_required
def download_report():

    pdf = canvas.Canvas("Prediction_Report.pdf")

    pdf.setTitle("Prediction Report")

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, 800, "Customer Prediction Report")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 760, f"User : {current_user.name}")
    pdf.drawString(50, 740, "Generated by SegmentAI")

    pdf.save()

    return send_file(
        "Prediction_Report.pdf",
        as_attachment=True
    )

if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8080))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
