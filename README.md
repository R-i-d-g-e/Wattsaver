# WattSaver — Energy Monitoring System

> Smarter Energy Starts Here

## INTRODUCTION.

WATTSAVER is a smart energy analysis system designed to help users better understand and manage their electricity consumption. In many households and small businesses, electricity usage is often untracked at the appliance level, leading to high bills, energy wastage, and inefficient decision-making.
WATTSAVER addresses this problem by providing a simple, data-driven platform where users can input appliance usage, analyze consumption patterns, and receive insights that help reduce energy costs and improve efficiency. The system empowers users to take control of their energy usage in a smarter and more informed way.

## HOW WATTSAVER IS BUILT

WATTSAVER is designed as a modular system combining data input, processing, storage, and visualization:

| Feature | Description |
|---|---|
| Appliance Input | Add appliances with name, category, power (W), hours/day, days/week |
| Energy Calculator | Computes daily, weekly & monthly kWh per appliance |
| Cost Estimation | Estimates bills in KES using configurable Kenya Power tariff |
| Visualization Dashboard | Doughnut, bar, line & polar charts via Chart.js |
| Smart Recommendations | Detects wastage patterns, suggests savings per appliance |
| Usage Pattern Analysis | Peak load analysis by time of day |
| Multi-User System | Each user has isolated data with secure login |
| Data Storage | SQLite database for persistent tracking |

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
 ## Challenges Faced
During the development of WATTSAVER, several challenges were encountered:
•	Accurate Energy Calculations
Ensuring correct conversion between power ratings, usage time, and energy consumption.
•	Data Management
Designing a system that efficiently stores and retrieves large amounts of usage data.
•	User-Friendly Interface
Making the system simple enough for non-technical users to understand and use.
•	Visualization Complexity
Presenting energy data in a clear and meaningful way through graphs and comparisons.
•	System Integration
Combining different modules (input, processing, storage, and visualization) into one smooth workflow.
## Accomplishments Achieved
Despite the challenges, the project achieved several important milestones:
•	Successfully developed a working system for tracking appliance energy usage
•	Implemented accurate energy consumption and cost estimation calculations
•	Created a structured data storage system for tracking historical usage
•	Built visualization features to display energy trends and comparisons
•	Designed a system capable of analyzing usage patterns and identifying inefficiencies
•	Enabled multi-user functionality for personalized data tracking
These accomplishments demonstrate the system’s ability to provide practical energy insights and support better energy management.

## What’s Next for WATTSAVER
Future improvements and expansions for WATTSAVER include:
•	Real-time Data Integration
Connecting the system to smart meters or IoT devices for automatic data collection
•	Mobile Application Development
Making WATTSAVER accessible on smartphones for convenience
•	AI-Based Recommendations
Enhancing the recommendation system using machine learning
•	Cloud Integration
Allowing users to access their data from anywhere
•	Advanced Analytics
Providing deeper insights such as predictive energy usage and anomaly detection
•	Integration with Renewable Energy Systems
Supporting solar energy analysis and optimization
## Conclusion
WATTSAVER is a practical and impactful solution to the growing challenge of energy management. By combining data collection, analysis, and visualization, the system enables users to better understand their electricity usage and make informed decisions.
As energy costs continue to rise and efficiency becomes more important, systems like WATTSAVER play a key role in promoting smarter energy consumption. With future improvements, the platform has the potential to evolve into a powerful tool for both individuals and businesses.

