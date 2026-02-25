# 🌌 Galaxy Schema: The Cross-Process Layer

## 📖 How it Works
A Galaxy Schema (or Fact Constellation) consists of **multiple Fact tables** sharing common (conformed) Dimensions. It allows analysis across different business processes that wouldn't normally be combined in a single star.

## 🚀 Why it is Important (Industry)
- **Interconnected Insights**: It moves from "Siloed Analytics" (Sales vs Logistics) to "Holistic Analytics" (How Logistics affects Sales).
- **Process Correlation**: Essential for finding hidden patterns across different operational streams.

## 🧪 Business Case in this Lab (Customer Experience)
We bridge **Logistics** (Orders & Deliveries) with **Customer Sentiment** (Reviews).
- **Metric**: `fct_order_experience`.
- **Insight**: We correlate `delivery_delay_days` with `review_score`. This allows the business to quantify exactly how much money is lost (in churn or negative reviews) due to logistics inefficiencies.

## 💡 Pro Tip for Beginners
When you start seeing the same dimensions (Customer, Date, Product) appearing in different dashboards, you are already building a Galaxy Schema. Focus on ensuring your dimensions have the same **Grain** and **ID structure** (Conformed Dimensions) so they can be joined reliably across facts.
