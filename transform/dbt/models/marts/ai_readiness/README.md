# 🤖 AI Readiness: The Intelligence Layer

## 📖 How it Works
This layer is specifically designed to feed **Machine Learning models**. We take raw transactional data and transform it into **Feature Vectors** (like Spent, Recency, and Frequency) that an AI can understand and use for prediction.

## 🚀 Why it is Important (Industry)
- **Feature Engineering**: Bridging the gap between "Data Engineering" and "Data Science".
- **Standardized Context**: Ensuring the LLM or ML model receives the same clean data used in BI, preventing "Data Drift".
- **Real-time Prediction**: Providing the historical snapshots required for backtesting models.

## 🧪 Business Case in this Lab (Churn Prediction)
We created `fct_customer_churn_features`.
- **Goal**: Identify customers who haven't ordered in 90+ days.
- **Value**: By surfacing "Recency" and "Lifetime Value" as ready-to-use columns, we enable the marketing team to trigger automated retention campaigns (Email, Coupons) without requiring a data scientist to re-clean the data.

## 💡 Pro Tip for Beginners
Think of your Marts not just as "Dashboard sources", but as "AI context". Clean, well-modeled data is 80% of the work in any AI project. If your warehouse is a mess, your AI will be too.
