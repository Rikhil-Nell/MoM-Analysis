# Directory Structure

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
