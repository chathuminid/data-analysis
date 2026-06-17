import pandas as pd
import matplotlib.pyplot as plt
data = pd.read_csv("Sales-Export_2019-2020.csv")

print(data.head())
print(data.shape)
print (data.describe())
print(data.describe(include='all'))
print(data.isnull().sum())

print("--- Data Summary ---")
print(data.info())

print("--- Category Counts ---")
print(data['category'].value_counts())

#clean up column names (removes hidden spaces and makes them lowercase)
data.columns = data.columns.str.strip().str.lower()

#print the columns to the terminal
print("--- detected Columns ---")
print(data.columns.tolist())
print("-" * 25)

#Automatically find the right columns even with different names
value_col = next(
    (col for col in data.columns if "value" in col or "price" in col), None
)
cost_col = next((col for col in data.columns if "cost" in col), None)
category_col = next(
    (col for col in data.columns if "category" in col or "type" in col),None
)


#3.fix data types convert text to numbers
if value_col:
    data[value_col] = (
        data[value_col]
        .astype(str)
        .str.replace("€","",regex=False)
        .str.replace("$","",regex=False)
        .str.replace(",","",regex=False)
        .str.strip()
    )
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")

if cost_col:
    #Do the same cleaning for the cost column
    data[cost_col] = (
        data[cost_col]
        .astype(str)
        .str.replace("€","",regex=False)
        .str.replace("$","",regex=False)
        .str.replace(",","",regex=False)
        .str.strip()
    )
    data[cost_col] = pd.to_numeric(data[cost_col], errors="coerce")

#4. print the statistical summary(Min max average) & Calculate Profit Metrics(Profit = Revenue - Cost and Profit Margin = (Profit/Revenue)*100)
print("--- Numerical Data summary ---")
if value_col and cost_col:
    print(data[[value_col, cost_col]].describe())

    #NEW ANALYSIS STEP
    print("\n--- Calculating Profit Metrics ---")
    # Calculate absolute profit
    data["profit"] = data[value_col] - data[cost_col]

    #calculate profit margin percentage safety (avoid dividing by zero)
    data["Profit_margin_%"] = (data["profit"]/data[value_col])*100

    #NEW FEATURE ENGINEERING: Customer Habits
    customer_col = next(
        (col for col in data.columns if "customer" in col or "client" in col or "id" in col), None
    )

    if customer_col:
        print("\n--- Analyzing Customer Habits ---")

        #1. Purchase Frequency
        purchase_frequency = data.groupby(customer_col).size().reset_index(name='purchase_count')

        #2. Total spend
        total_spend = data.groupby(customer_col)[value_col].sum().reset_index(name='total_customer_spend')

        #3.add this new dats to main data(merging)
        data = pd.merge(data, purchase_frequency, on=customer_col, how='left')
        data = pd.merge(data, total_spend, on=customer_col, how='left')

        print("Success! Added 'Purchase_count' and 'total_customer_spend' features.")


        # 3. Calculate Top 10 VIPs
        print("\n--- Top 10 VIP Customers ---")
        top_10_vips = total_spend.sort_values(by="total_customer_spend", ascending=False).head(10)
        print(top_10_vips.reset_index(drop=True))

        # 4. Generate the VIP Chart immediately
        print("\n--- Generating VIP Customer Chart ---")
        plt.figure(figsize=(10, 5))
        
        # Convert IDs to text for the chart
        top_10_vips[customer_col] = top_10_vips[customer_col].astype(str)

        plt.bar(
            top_10_vips[customer_col], 
            top_10_vips["total_customer_spend"], 
            color="gold", 
            edgecolor="black"
        )

        plt.title("Top 10 VIP Customers by Total Spend")
        plt.xlabel("Customer ID")
        plt.ylabel("Total Spend")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig("top_10_vip_customers.png")
        plt.close()
        print("Success! Created 'top_10_vip_customers.png'")
        
    else:
        print("Could not find a customer column to analyze habits.")

    # Group by category to see total performance
    if category_col:
        category_perf = (
            data.groupby(category_col)[[value_col, cost_col, "profit"]]
            .sum()
            .sort_values(by="profit", ascending=False)
        )
        print("\nTotal Financial Performance by Category:")
        print(category_perf)

else:
    print("Could not find value or cost columns to calculate profit.")

#5. Create and save data charts
print("\n--- Generating Visual Chart ---")
if category_col:
    #Chart 1: Category count (Existing)
    plt.figure(figsize=(10, 5))
    data[category_col].value_counts().plot(
        kind="bar", color="skyblue", edgecolor="black"
    )
    plt.title("Category Distribution(Total Sales Count)")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    #plt.show()
    plt.savefig('category_distribution.png')
    plt.close() #clears the sheet for the next chart

    # --- NEW CHART : Profit by category ---
    if "profit" in data.columns:
        plt.figure(figsize=(10, 5))

        #Group and granb just the profit for charting
        category_perf["profit"].sort_values(ascending=True).plot(
            kind="barh", color="Lightgreen", edgecolor="black"
        )

        plt.title("Total profit by Product Category (EUR)")
        plt.xlabel("Profit (€)")
        plt.ylabel("Category")
        plt.tight_layout()

        # Save this as a brand new image file
        plt.savefig("profit_by_category.png")
        print(
            "Success! Created 'category_distribution.png and 'profit_by_category.png'"
        )

else:
    print("Could not find a category column to plot.")


#6. ---NEW PHASE: TIME TRENDS ANALYSIS ---
print("\n--- Generating Time-Series Chart ---")

# Automatically find a column with 'date' or 'time' in the name
date_col = next(
    (col for col in data.columns if "date" in col or  "time" in col), None
)

if date_col:
    # Convert text column to actual python datetime format
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")

    # Drop any rows where the date couldn't be read properly
    time_data = data.dropna(subset=[date_col])

    #Group sales values by year and Month
    monthly_sales =(
        time_data.groupby(time_data[date_col].dt.to_period("M"))[value_col]
        .sum()
        .reset_index()
    )

    # convert the period back to string so matplotlib can easily map it
    monthly_sales[date_col] = monthly_sales[date_col].astype(str)

    #Covert the period back to string to matplotlib can easily map it
    monthly_sales[date_col] = monthly_sales[date_col].astype(str)

    #plot the line chart
    plt.figure(figsize=(12, 5))
    plt.plot(
        monthly_sales[date_col],
        monthly_sales[value_col],
        marker="o",
        color="orange",
        linewidth=2
    )
    plt.title("Total Sales Trend Over Time")
    plt.xlabel("Month")
    plt.ylabel("Total Revenue")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    plt.savefig("sales_trend_over_time.png")
    plt.close()
    print("Success! Created 'sales_trend_over_time.png'")
else:
    print("Could not find a date column to analyze time trends.")

#7. ---VIP Customer Visualization ---
print("\n--- Generating VIP Customer Chart ---")

#we only run this if we successfully found customers earlier
if customer_col and 'top_10_vips' in locals():
    plt.figure(figsize=(10, 5))

    #convert customer IDs to text so the chart doesn't treat them like standard math numbers
    top_10_vips[customer_col] = top_10_vips[customer_col].astype(str)

    #Create a gold bar chart
    plt.bar(
        top_10_vips[customer_col],
        top_10_vips["total_customer_spend"],
        color="gold",
        edgecolor="black"
    )

    plt.title("Top 10 VIP Customers by Total spend (€)")
    plt.xlabel("Customer ID")
    plt.ylabel("Total spend (€)")

    #Rotate the customer IDs slightly so they don't overlap
    plt.xticks(rotation=45)

    #Automatically adjust spacing
    plt.tight_layout()

    #Save the new chart
    plt.savefig("top_10_vip_customers.png")
    plt.close()
    print("Success! Created 'top_10_vip_customer.png'")
else:
    print("Could not generate VIP chart: Missing customer data.")