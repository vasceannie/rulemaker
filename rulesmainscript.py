import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd

def select_source_file():
    """Function to select source file."""
    path = filedialog.askopenfilename(title="Select Source CSV", filetypes=[("CSV files", "*.csv")])
    source_file_path.set(path)

def select_output_file():
    """Function to select output file location."""
    path = filedialog.asksaveasfilename(title="Select Output CSV Location", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    output_file_path.set(path)

def transform_data():
    """Function to process the source file and save the output."""
    # Read the source file ensuring SB_LIMIT_AMT is read as string
    df = pd.read_csv(source_file_path.get(), dtype={'SB_LIMIT_AMT': str})

    # Placeholder for transformed data
    transformed_data = []

    # Group by Rule Group and Rule Name
    for (sb_aprv_level, emplid), group in df.groupby(['SB_APRV_LEVEL', 'EMPLID']):
        
        rule_group_name = f"DOA Approval: Level {sb_aprv_level}"
        rule_name = f"DOA RULE: {emplid}"
        
        # Aggregate department IDs
        deptids = "|".join([f"DeptID|oneOf||{'|'.join(group['DEPTID_CF'].unique())}"])
        
        # Handle the spend values stored as text (assuming unique values per group)
        spend_values = group['SB_LIMIT_AMT'].iloc[0].split('-')
        if len(spend_values) == 1:
            lower_limit = 0.01
            upper_limit = float(spend_values[0])
        else:
            lower_limit = float(spend_values[0]) + 0.01
            upper_limit = float(spend_values[1])
        document_total = f"Between|{lower_limit}|{upper_limit}|USD"
        
        business_unit = "equalTo|CHXCO"
        
        # Append to the transformed data
        transformed_data.extend([
            [rule_group_name, rule_name, "DocumentTotal", document_total],
            [rule_group_name, rule_name, "CustomFieldValueSingle", deptids],
            [rule_group_name, rule_name, "BusinessUnit", business_unit]
        ])

    # Create a DataFrame from the transformed data
    output_df = pd.DataFrame(transformed_data, columns=["Rule Group Name", "Rule Name", "Type", "Value"])

    # Save the transformed data to the output file
    output_df.to_csv(output_file_path.get(), index=False)

    # Update the progress bar
    progress_bar['value'] = 100

# Create main application window
root = tk.Tk()
root.title("ChicoDOA Transformer - CSV")

# Initialize variables to store file paths
source_file_path = tk.StringVar()
output_file_path = tk.StringVar()

# Create UI elements
source_file_button = tk.Button(root, text="Select Source CSV", command=select_source_file)
source_file_button.pack(pady=20)

output_file_button = tk.Button(root, text="Select Output CSV Location", command=select_output_file)
output_file_button.pack(pady=20)

transform_button = tk.Button(root, text="Transform Data", command=transform_data)
transform_button.pack(pady=20)

progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(pady=20)

root.mainloop()
