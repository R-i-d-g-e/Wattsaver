# ⚡ WattSaver — Energy Monitoring System

> Smarter Energy Starts Here

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## Features

| Feature | Description |
|---|---|
| 🔌 Appliance Input | Add appliances with name, category, power (W), hours/day, days/week |
| ⚡ Energy Calculator | Computes daily, weekly & monthly kWh per appliance |
| 💰 Cost Estimation | Estimates bills in KES using configurable Kenya Power tariff |
| 📊 Visualization Dashboard | Doughnut, bar, line & polar charts via Chart.js |
| 💡 Smart Recommendations | Detects wastage patterns, suggests savings per appliance |
| 📈 Usage Pattern Analysis | Peak load analysis by time of day |
| 👥 Multi-User System | Each user has isolated data with secure login |
| 🗄️ Data Storage | SQLite database for persistent tracking |

## System Architecture

```
wattsaver/
├── app.py              # Flask app, routes, models, business logic
├── requirements.txt    # Python dependencies
├── wattsaver.db        # SQLite database (auto-created on first run)
└── templates/
    ├── index.html      # Landing + login/register page
    └── dashboard.html  # Full dashboard UI
```

## Energy Calculation Formulas

```
Daily kWh  = (Power_W × Hours_per_day) / 1000
Weekly kWh = Daily_kWh × Days_per_week
Monthly kWh = Daily_kWh × (Days_per_week / 7) × 30
Monthly Cost (KES) = Monthly_kWh × Cost_per_kWh
```

Default Kenya Power rate: **KES 25.00/kWh** (configurable per user)

## Categories Supported
- Heating/Cooling (AC, fans, heaters)
- Lighting
- Kitchen (fridge, microwave, cooker)
- Entertainment (TV, gaming, speakers)
- Office/Work (laptop, router, monitor)
- Water Heating
- Other

## Team
- Alvin Ridge — Lead Developer, Backend
- Brain Wanjala — Data & Visualization
- Alex Mokami — UI/Visualization
- Griffin Were — Documentation & Testing
- Emmanuel Mwedwa — Optimization
