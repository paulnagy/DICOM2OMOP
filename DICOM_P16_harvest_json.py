import pandas as pd
import json
import os

def json_to_pandas_dataframe(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        id = data.get('id', '')
        version = data.get('version', '')
        status = data.get('status', '')
        description = data.get('description', '')

        compose_include_data = data.get('compose', {}).get('include', [])
        compose_include_list = []

        for include in compose_include_data:
            system = include.get('system', '')
            for concept in include.get('concept', []):
                concept.update({'system': system, 'id': id, 'version': version, 'status': status, 'description': description})
                compose_include_list.append(concept)

        return pd.DataFrame(compose_include_list)

    except Exception as e:
        print(f"An error occurred processing {json_file_path}: {e}")
        return pd.DataFrame()

# Directory containing JSON files
directory = './sourceandrenderingpipeline/valuesets/valuesets/fhir/json/'

# List all JSON files in the directory
json_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.json')]

# Process each file and combine into a single DataFrame
df_combined = pd.DataFrame()
for file in json_files:
    df = json_to_pandas_dataframe(file)
    df_combined = pd.concat([df_combined, df], ignore_index=True)

# Save the combined DataFrame as CSV and Parquet
df_combined.to_csv('./files/fhir_valuesets.csv', index=False)
df_combined.to_parquet('./files/fhir_valuesets.parquet', index=False)

print("Files saved: fhir_valuesets.csv and fhir_valuesets.parquet")