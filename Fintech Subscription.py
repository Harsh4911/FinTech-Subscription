import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile

# 1. Dataset ko Extract aur Load karna
zip_path = 'Fintech Subscription.zip'
csv_inside_zip = 'WA_Fn-UseC_-Telco-Customer-Churn.csv'

with zipfile.ZipFile(zip_path, 'r') as z:
    with z.open(csv_inside_zip) as f:
        df = pd.read_csv(f)

print("--- Dataset Loaded Successfully ---")

# 2. Data Cleaning & Preparation (No Inplace, Safe for Copy-on-Write)
# Churn column ko binary banana
df['Churn_Numeric'] = np.where(df['Churn'] == 'Yes', 1, 0)

# TotalCharges ko numeric banana aur missing values ko fill karna bina kisi warning ke
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
median_total_charges = df['TotalCharges'].median()
df['TotalCharges'] = df['TotalCharges'].fillna(median_total_charges)

# 3. Dynamic Cohort Creation
cohort_data = df.groupby(['Contract', 'tenure']).agg(
    Total_Users=('customerID', 'count'),
    Churned_Users=('Churn_Numeric', 'sum')
).reset_index()

# Base Size nikalna bina pipeline break kiye
cohort_data['Base_Size'] = cohort_data.groupby('Contract')['Total_Users'].transform('max')
cohort_data['Active_Users'] = cohort_data['Total_Users']
cohort_data['Retention_Rate'] = cohort_data['Active_Users'] / cohort_data['Base_Size']

# 4. Cohort Retention Matrix (Pivot Table)
retention_matrix = cohort_data.pivot(index='Contract', columns='tenure', values='Retention_Rate')
retention_matrix_filtered = retention_matrix.iloc[:, :24] # Pehle 24 mahine ka view

# 5. Graph Plotting
plt.figure(figsize=(16, 6))
sns.heatmap(
    retention_matrix_filtered, 
    annot=True, 
    fmt='.1%', 
    cmap='YlGnBu', 
    cbar_kws={'label': 'Retention Rate (%)'},
    linewidths=0.5
)

plt.title('Subscription Cohort Retention Heatmap', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Lifecycle Month (Tenure)', fontsize=12)
plt.ylabel('Subscription Contract Type', fontsize=12)
plt.tight_layout()
plt.show()

# 6. Executive Summary (LTV Analysis)
print("\n--- Executive Summary: Average LTV by Contract Type ---")
df['Estimated_LTV'] = df['MonthlyCharges'] * df['tenure']
ltv_summary = df.groupby('Contract').agg(
    Avg_Monthly_Charges=('MonthlyCharges', 'mean'),
    Avg_Tenure_Months=('tenure', 'mean'),
    Avg_Estimated_LTV=('Estimated_LTV', 'mean')
).round(2)
print(ltv_summary)



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import zipfile

# 1. Base Data Load karna
zip_path = 'Fintech Subscription.zip'
csv_inside_zip = 'WA_Fn-UseC_-Telco-Customer-Churn.csv'
with zipfile.ZipFile(zip_path, 'r') as z:
    with z.open(csv_inside_zip) as f:
        df = pd.read_csv(f)

df['Churn_Numeric'] = np.where(df['Churn'] == 'Yes', 1, 0)

# FIXED LINE 84 ISSUE: Pehle numeric banaya, fir median nikala, fir fill kiya
total_charges_numeric = pd.to_numeric(df['TotalCharges'], errors='coerce')
median_val = total_charges_numeric.median()
df['TotalCharges'] = total_charges_numeric.fillna(median_val)

df['Estimated_LTV'] = df['MonthlyCharges'] * df['tenure']

# 2. Risk Matrix Classification
value_threshold = df['MonthlyCharges'].quantile(0.70)
df['Customer_Value'] = np.where(df['MonthlyCharges'] >= value_threshold, 'High-Value', 'Standard-Value')
df['Risk_Level'] = np.where(df['Contract'] == 'Month-to-month', 'High-Risk', 'Low-Risk')
df['Strategic_Segment'] = df['Customer_Value'] + " / " + df['Risk_Level']

# 3. Dynamic Retention Budget Recommendation
def calculate_retention_budget(row):
    if row['Strategic_Segment'] == 'High-Value / High-Risk':
        return row['MonthlyCharges'] * 0.20  
    elif row['Strategic_Segment'] == 'Standard-Value / High-Risk':
        return row['MonthlyCharges'] * 0.10  
    else:
        return row['MonthlyCharges'] * 0.05  

df['Max_Retention_Budget_USD'] = df.apply(calculate_retention_budget, axis=1)

# 4. Executive Summary Matrix Table
print("\n" + "="*60)
print(" FINANCIAL OPTIMIZATION MATRIX FOR EXEC TEAM ")
print("="*60)

summary_matrix = df.groupby('Strategic_Segment').agg(
    Customer_Count=('customerID', 'count'),
    Current_Churn_Rate=('Churn_Numeric', lambda x: f"{round(x.mean()*100, 1)}%"),
    Avg_Monthly_Revenue=('MonthlyCharges', 'mean'),
    Total_Risk_Value_LTV=('Estimated_LTV', 'sum'),
    Recommended_Per_User_Budget=('Max_Retention_Budget_USD', 'mean')
).round(2).reset_index()

print(summary_matrix.to_string(index=False))

# 5. Financial Risk vs Retention Budget Plot (Warning Fixed)
plt.figure(figsize=(12, 6))

# Subplot 1: Total Financial Risk LTV
plt.subplot(1, 2, 1)
sns.barplot(
    data=summary_matrix, 
    x='Strategic_Segment', 
    y='Total_Risk_Value_LTV', 
    hue='Strategic_Segment', # Hue assign kiya warning hatane ke liye
    palette='Reds_r', 
    legend=False             # Extra legend ko hide kiya
)
plt.title('Total Financial Value at Risk (LTV)', fontsize=12, fontweight='bold')
plt.xticks(rotation=20, ha='right')
plt.ylabel('Total Value in USD')

# Subplot 2: Recommended Budget Allocation
plt.subplot(1, 2, 2)
sns.barplot(
    data=summary_matrix, 
    x='Strategic_Segment', 
    y='Recommended_Per_User_Budget', 
    hue='Strategic_Segment', # Hue assign kiya warning hatane ke liye
    palette='GnBu_r', 
    legend=False             # Extra legend ko hide kiya
)
plt.title('Recommended Retention Budget per User', fontsize=12, fontweight='bold')
plt.xticks(rotation=20, ha='right')
plt.ylabel('Budget per Month (USD)')

plt.tight_layout()
plt.show()

# Processed data ko Power BI ke liye export karna
df.to_csv('Fintech_Retention_PowerBI_Ready.csv', index=False)
print("Dashboard ke liye data successfully export ho gaya hai: 'Fintech_Retention_PowerBI_Ready.csv'")