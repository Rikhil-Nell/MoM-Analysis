# MoM Analysis

MoM Analysis is a data-driven analytics and coupon strategy platform for Indian restaurants, designed to help businesses combat margin pressures from food delivery platforms and optimize in-store performance. The project provides tools for analyzing key performance indicators (KPIs) related to customers, orders, and products, and generates actionable coupon strategies to increase footfall and customer frequency.

## Features

- **KPI Data Analysis**: Analyze customer behavior, order patterns, and product performance using Jupyter notebooks and CSV datasets.
- **Coupon Strategy Generation**: Automated recommendations for coupon campaigns based on data insights.
- **Streamlit Dashboard**: Interactive web app for exploring KPIs and generating strategies.
- **Extensible Structure**: Easily add new analyses or data sources.

## Directory Structure

MoM Analysis/
│
├── analysis/
│   ├── customer_analysis.ipynb
│   ├── order_analysis.ipynb
│   └── product_analysis.ipynb
│
├── results/
│    ├── customer_analysis/
│    │   └── Customer_KPIs_KnownPhonesOnly.csv
│    ├── order_analysis/
│    │   ├── Invoice_Aggregation.csv
│    │   ├── Product_Co_occurence_Matrix.csv
│    │   └── Product_Co_occurence_Matrix_filtered.csv
│    └── product_analysis/
│        ├── yearly/
│        │   ├── Yearly_Product_Performance.csv
│        │   └── Yearly_Top_Selling_Items.csv
│        ├── monthly/
│        │   ├── Monthly_Product_Performance.csv
│        │   └── Monthly_Top_Selling_Items.csv
│        ├── daily/
│        │   ├── Daily_Product_Performance.csv
│        │   ├── Daily_Item_Sales_Pivot.csv
│        │   └── Average_Performance_By_DayOfWeek.csv
│        └── hourly/
│            ├── Hourly_Product_Performance.csv
│            ├── Hourly_Item_Sales_Pivot.csv
│            └── Average_Performance_By_Hour.csv
│
├── prompt.txt
├── app.py
├── main.py
└── settings.py

## Getting Started

### Prerequisites

- Python 3.13+
- [pip](https://pip.pypa.io/en/stable/)
- (Recommended) [virtualenv](https://virtualenv.pypa.io/en/latest/)

### Installation

1. Clone the repository:

    ```sh
    git clone <repo-url>
    cd MoM\ Analysis
    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up your `.env` file with the required API keys.

### Running the App

To launch the Streamlit dashboard:

```sh
streamlit run [app.py](http://_vscodecontentref_/11)
```

## Running Analyses

Open the notebooks in the `analysis/` folder using Jupyter or VS Code to explore and extend the KPI analyses.

## Usage

- Use the sidebar in the Streamlit app to explore KPI structures and
  run analyses.
- Review generated coupon strategies and recommendations based on
  your restaurant's data.
