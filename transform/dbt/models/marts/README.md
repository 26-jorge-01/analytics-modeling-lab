# 🎯 Marts: The Analytical Gold Layer

## 📖 Strategy
The Marts layer is where raw data is turned into **Business Intelligence**. In this lab, we don't just provide one type of model; we demonstrate a **Multi-Paradigm** strategy to solve different business needs.

### 📚 The Modeling Handbook
| Paradigm | Best For | Technical implementation | Folder |
| :--- | :--- | :--- | :--- |
| **Star Schema** | Dashboard speed & Analysts | Denormalized Wide Tables | [star/](./star/) |
| **Snowflake** | Hierarchies & Data Integrity | Normalized Multi-level Dims | [snowflake/](./snowflake/) |
| **Galaxy Schema** | Cross-Process Correlation | Shared Conformed Dimensions | [galaxy/](./galaxy/) |
| **AI Readiness** | Machine Learning Training | Feature Engineering / Recency | [ai_readiness/](./ai_readiness/) |

## 🚀 Why This Matters
A mature data team shouldn't be dogmatic about one modeling style.
- **Star** is king for performance.
- **Snowflake** is king for territory management.
- **Galaxy** is king for finding hidden business causes.

## 💡 How to navigate this folder
If you are looking for a specific metric:
- **Sales & Orders**: Go to [Star Schema](./star/).
- **Logistics vs Reviews**: Go to [Galaxy Schema](./galaxy/).
- **ML Features**: Go to [AI Readiness](./ai_readiness/).
