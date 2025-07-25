Cash Flow Seasonality OptimizerA comprehensive, interactive dashboard built with Python and Streamlit to analyze, forecast, and optimize business cash flow. 

This tool helps users uncover seasonal patterns, project future financial performance, and test business scenarios to make informed decisions.

Features:

Interactive Dashboard: A clean, user-friendly web interface built with Streamlit for easy navigation and analysis.

Seasonal Analysis: Automatically decomposes time-series data to identify and visualize underlying trends, seasonal patterns, and residuals.

KPI Tracking: Calculates and displays key performance indicators like Days Sales Outstanding (DSO), Days Payable Outstanding (DPO), and the Cash Conversion Cycle.

Statistical Forecasting: Generates future cash flow projections using multiple models, including Ensemble, Exponential Smoothing, and Seasonal Naive methods.

Scenario & Stress Testing: Allows users to model how their cash flow might change under different optimistic, pessimistic, or conservative business scenarios.

Actionable Insights: Provides automated, plain-English recommendations based on the financial data to guide decision-making.

Project Structure:

The project is organized into a modular structure for clarity and maintainability.cash-flow-project/

├── data/

│   └── sample_data.csv

├── dashboard/

│   └── streamlit_app.py

├── output/

│

├── data_generator.py

├── data_processor.py

├── analyzer.py

├── forecaster.py

├── visualizer.py

├── insights_generator.py
│

├── main.py

└── requirements.txt

How to Run:

There are two ways to run this project: as a command-line report generator or as an interactive web dashboard.


Prerequisites

   First, install all the necessary libraries from the requirements.txt file.pip install -r requirements.txt
   Generate Sample DataBefore running any analysis, you need to generate the sample data file.python data_generator.py
   
   
1.Running the Interactive Dashboard (Recommended)

To launch the interactive web application, run the following command from your main project directory:streamlit run dashboard/streamlit_app.py

Your web browser should automatically open a new tab with the live dashboard.


2.Running the Automated Report

To run the entire analysis pipeline from the command line and save all reports, charts, and data files to the output/ folder, use this command:python main.py


Dependencies

All required Python libraries are listed in the requirements.txt file.

Key libraries include:

streamlit

pandas

numpy

matplotlib

seaborn

plotly

scipy

statsmodels
