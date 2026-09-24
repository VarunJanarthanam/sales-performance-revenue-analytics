# Sales Performance & Revenue Analytics — Superstore

An end-to-end retail analytics project that cleans and validates order data, analyzes business questions with SQL and Python, and presents the results in an interactive dashboard.

**[→ View the live interactive dashboard](https://VarunJanarthanam.github.io/sales-performance-revenue-analytics/dashboard/superstore_dashboard.html)**

## Project Overview

| Item | Details |
|---|---|
| Dataset | Sample Superstore — US and Canada retail orders |
| Data volume | 10,194 order line items · 5,111 orders · 804 customers |
| Period covered | January 2023 – December 2026 |
| Technologies | Python (pandas), SQLite/SQL, Chart.js |
| Dashboard | Self-contained HTML dashboard |

The project follows an analytics workflow: validate the source data, investigate business questions with SQL, and communicate the results through an interactive dashboard.

## Repository Structure

```text
.
├── data/
│   ├── sample_-_superstore.xlsx   # Raw source data
│   ├── superstore_clean.csv       # Cleaned, analysis-ready data
│   └── superstore.db              # SQLite database (orders, people, returns)
├── scripts/
│   ├── 01_clean_data.py           # Data cleaning and quality checks
│   ├── 02_sql_analysis.sql        # 12 business-question queries
│   └── 03_build_dashboard.py      # Dashboard generation
├── dashboard/
│   └── superstore_dashboard.html  # Interactive dashboard
├── requirements.txt
└── README.md
```

## Workflow and Implementation

### 1. Data Cleaning and Validation

The `01_clean_data.py` script loads the `Orders`, `People`, and `Returns` sheets and performs data-quality checks.

- Checked for duplicate rows and duplicate `Row ID` values; none were found.
- Checked for logical issues including ship dates earlier than order dates, negative sales, and non-positive quantities; none were found.
- Standardized `Postal Code` values into a consistent zero-padded string format to handle numeric US codes and alphanumeric Canadian codes.
- Flagged 32 Product IDs reused across different product names and 11 duplicate Order ID + Product ID line items. These were retained and documented rather than removed without sufficient context.
- Created analysis fields including `Profit Margin`, `Days to Ship`, `Order Year`, `Order Year-Month`, `Is Loss`, and `Is Returned`.

The script outputs a cleaned CSV and a SQLite database with `orders`, `people`, and `returns` tables.

### 2. SQL Analysis

The `02_sql_analysis.sql` file contains 12 queries covering:

- Headline KPIs and monthly/year-over-year trends
- Region, category, and segment comparisons
- Profitability by discount band
- Highest- and lowest-performing products and customers
- Shipping-mode trade-offs
- Return-rate impact
- State-level performance

### 3. Interactive Dashboard

The `03_build_dashboard.py` script uses pandas to aggregate the cleaned data and generates a self-contained HTML dashboard using Chart.js. The dashboard has four tabs:

- **Overview**
- **Profitability**
- **Customers & Products**
- **Geography**

The HTML dashboard does not require a backend server.

## Key Findings

### Revenue increased, while margin remained around 12–13% in the later years

| Year | Revenue | Profit | Margin |
|---|---:|---:|---:|
| 2023 | $494,040 | $51,684 | 10.5% |
| 2024 | $472,993 | $62,021 | 13.1% |
| 2025 | $613,934 | $82,665 | 13.5% |
| 2026 | $745,568 | $95,926 | 12.9% |

### Higher discount bands were associated with substantial losses

| Discount band | Margin |
|---|---:|
| 0% (no discount) | 29.6% |
| 1–20% | 11.9% |
| 21–40% | -15.3% |
| 41–60% | -40.8% |
| 60%+ | -122.6% |

### Furniture sub-categories included notable losses

Tables recorded approximately **-$17.8K** in profit and Bookcases approximately **-$3.6K**. Both sub-categories also had above-average discount rates in this dataset.

### Several states had positive revenue but negative profit

- Texas: approximately -$25.7K profit on $170K revenue
- Pennsylvania: approximately -$15.6K profit
- Illinois: approximately -$12.6K profit
- Ohio: approximately -$17.0K profit

The Central region had the lowest margin among the four regions at **7.9%**.

## Recommendations Drawn from the Analysis

1. Review discretionary discount policies, particularly for Furniture and Technology Machines, in light of the observed relationship between discount bands and profitability.
2. Audit pricing and freight costs in Texas, Pennsylvania, Illinois, and Ohio, where the analysis showed high revenue alongside negative profit.
3. Review discounting practices for high-margin sub-categories such as Copiers, Labels, Paper, and Envelopes, which each showed margins above 40% in the analyzed data.

These are analysis-based recommendations, not proof that any single factor caused the observed results.

## How to Reproduce

### Requirements

Python dependencies are listed in `requirements.txt`. The SQL analysis uses SQLite.

1. Clone the repository:

   ```bash
   git clone https://github.com/VarunJanarthanam/sales-performance-revenue-analytics.git
   cd sales-performance-revenue-analytics
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the data-cleaning script:

   ```bash
   cd scripts
   python 01_clean_data.py
   ```

4. Run the SQL queries against the generated database:

   ```bash
   sqlite3 ../data/superstore.db < 02_sql_analysis.sql
   ```

5. Generate the dashboard:

   ```bash
   python 03_build_dashboard.py
   ```

6. Open `dashboard/superstore_dashboard.html` in a browser. It is self-contained and does not require a server or build step.

## Data Notes

The source workbook and generated data files are included in the repository structure described above. Before publishing, ensure that the dataset's license and redistribution terms permit sharing. Document any changes to the source data and any assumptions used in the analysis.

## Author

**Varun Janarthanam**

- [GitHub Profile](https://github.com/VarunJanarthanam)
- [Portfolio Website](https://varunjanarthanam.github.io/varun-portfolio/)

---

*Project documentation reflects the reported implementation and analysis. Interpret findings in the context of the dataset, its coverage, and its data-quality notes.*
