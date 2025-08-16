import pandas as pd
import json
import os

def process_data():
    """
    Reads raw data from different sources, processes it, and
    combines it into a unified knowledge base CSV.
    """
    # Define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'ai_model', 'data')
    raw_data_dir = os.path.join(os.path.dirname(__file__), 'raw_data')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    knowledge_base = []

    # 1. Process Weather Data
    try:
        weather_df = pd.read_csv(os.path.join(raw_data_dir, 'imd_weather.csv'))
        for _, row in weather_df.iterrows():
            text = (f"On {row['Date']}, the weather in {row['City']} is expected to have a "
                    f"temperature of {row['Temperature']}°C, humidity of {row['Humidity']}%, "
                    f"and rainfall of {row['Rainfall_mm']}mm.")
            knowledge_base.append({'source': 'IMD Weather Portal', 'content': text})
    except FileNotFoundError:
        print("Warning: imd_weather.csv not found.")

    # 2. Process Market Data
    try:
        with open(os.path.join(raw_data_dir, 'agmarknet.json'), 'r') as f:
            market_data = json.load(f)
        for item in market_data:
            text = (f"The market price for {item['commodity']} in {item['market']} on "
                    f"{item['date']} is Rs. {item['price_per_quintal']} per quintal.")
            knowledge_base.append({'source': 'Agmarknet Portal', 'content': text})
    except FileNotFoundError:
        print("Warning: agmarknet.json not found.")

    # 3. Add sample policy data
    policy_text = ("The PM-KISAN scheme provides eligible farmers with an income support of "
                   "Rs. 6,000 per year in three equal installments. Verification is done via Aadhaar.")
    knowledge_base.append({'source': 'Government Policy Portal', 'content': policy_text})

    # Create DataFrame and save to CSV
    kb_df = pd.DataFrame(knowledge_base)
    output_path = os.path.join(output_dir, 'knowledge_base.csv')
    kb_df.to_csv(output_path, index=False)
    
    print(f"Knowledge base successfully created at {output_path}")

if __name__ == '__main__':
    process_data()