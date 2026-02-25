# ⚙️ Ops: Infrastructure & Developer Experience

## 📖 How it Works
This folder contains the "Glue" that holds the project together:
- **`init_db/`**: SQL scripts that auto-configure Postgres on the first run.
- **`sqlfluff_lib/`**: Custom logic to make dbt and SQL linting work together seamlessly.
- **Local Tooling**: Scripts to simplify the developer experience.

## 🚀 Why it is Important (Industry)
- **Reproducibility**: A new developer should be able to run `.\make.bat up` and have a working local environment in minutes.
- **Consistency**: Linting ensures that 10 developers write code that looks like it was written by one person.
- **CI/CD Readiness**: This infrastructure is what allows our GitHub Actions to validate code before it is merged.

## 🧪 Use Case in this Lab
We customized the SQL linting process to handle dbt macros, which is a common pain point in modern data stacks. This ensures our repository maintains "Elite" code quality scores.

## 💡 Pro Tip for Beginners
Invest heavily in your "Ops" layer. The easier it is for you to run and test your code locally, the faster you will innovate and the fewer bugs you will ship.
