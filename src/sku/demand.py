import pandas as pd
import matplotlib.pyplot as plt
from src.app import create_patrol_app
from sqlalchemy.sql import text
from src.database.db import db  # Adjust the import as per your project structure

app = create_patrol_app()

def fetch_data():
    sql = text('SELECT demand_id, survey_id, user_id, city, ranking, quantity, sku_name FROM sku_demand_survey')
    result = db.session.execute(sql)
    data = [row._asdict() for row in result]
    return data

if __name__ == '__main__':
    with app.app_context():
        x=fetch_data()
        # print(x)
        df = pd.DataFrame(x)

# Aggregating the data by city and sku_name
        aggregated_data = df.groupby(['city', 'sku_name']).agg({'quantity': 'sum'}).reset_index()

        # Sort the data for better visualization
        aggregated_data.sort_values(by=['city', 'sku_name'], inplace=True)

        # Pivot the data for plotting
        pivot_table = aggregated_data.pivot(index='sku_name', columns='city', values='quantity')

        # Plot the data
        pivot_table.plot(kind='bar', figsize=(12, 8))
        print(pivot_table)
        # Adding titles and labels
        plt.title('Total Quantity of SKUs by City')
        plt.xlabel('SKU Name')
        plt.ylabel('Total Quantity')
        plt.xticks(rotation=45)
        plt.legend(title='City')

        # Show the plot
        plt.tight_layout()
        plot_path = "/Users/roshneematlani/Documents/USC/Spring'24/CSCI-578/Team Project/PATROL/src/sku/total_quantity_skus_by_city.png"
        plt.savefig(plot_path)

        # Close the plot to avoid display issues in the Mac terminal
        plt.close()

        print(plot_path)

                

