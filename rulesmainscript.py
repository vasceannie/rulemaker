import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd
import numpy as np

def select_source_file():
    """Function to select source file."""
    path = filedialog.askopenfilename(title="Select Source CSV", filetypes=[("CSV files", "*.csv")])
    source_file_path.set(path)

def select_output_file():
    """Function to select output file location."""
    path = filedialog.asksaveasfilename(title="Select Output CSV Location", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    output_file_path.set(path)

def calculate_limits(business_unit, sb_aprv_level):
    """Determine the lower and upper limits based on the business unit and approval level."""
    limits = {
        "CHICO": {
            1: (100000.01, 999999999.99),
            2: (20000.01, 100000.00),
            3: (500.01, 20000.00),
            4: (0.01, 500.00)
        },
        "FRSNO": {
            1: (100000.01, 999999999.99),
            2: (50000.01, 100000.00),
            3: (5000.01, 50000.00),
            4: (0.01, 5000.00)
        },
        "FRATH": {
            1: (100000.01, 999999999.99),
            2: (50000.01, 100000.00),
            3: (5000.01, 50000.00),
            4: (0.01, 5000.00)
        }
    }
    return limits[business_unit].get(sb_aprv_level, (0, 0))

def reverse_modify_business_unit(modified_business_unit):
    """Transform modified business unit values back to their original form."""
    reverse_replacements = {
        "CHXCO": "CHICO",
        "FRXNO": "FRSNO",
        "FRXTH": "FRSNO"
    }
    return reverse_replacements.get(modified_business_unit, modified_business_unit)

def modify_business_unit(business_unit):
    """Transform business unit values."""
    replacements = {
        "CHICO": "oneOf|CHXCO",
        "FRSNO": "oneOf|FRXNO",
        "FRATH": "oneOf|FRXTH"
    }
    return replacements.get(business_unit, business_unit)

def replace_text(string):
    if string == "CHICO" or string == "FRSNO" or string == "FRATH":
        # Replace the BU code with the intended conditional value(s)
        if string == "CHICO":
            string = "CHICO"
        elif string == "FRSNO":
            string = "FRSNO"
        elif string == "FRATH":
            string = "FRSNO"
        # Add more conditions if needed
        
    return string

def transform_data():
    """Function to process the source file and save the output."""
    df = pd.read_csv(source_file_path.get(), dtype={'SB_LIMIT_AMT': str})
    df['SB_APRV_LEVEL'] = df['SB_APRV_LEVEL'].astype('Int64')
    transformed_data = []

    # Group by 'DEPTID_CF' and 'SB_APRV_LEVEL' and aggregate the "Rule Approvers"
    grouped_df = df.groupby(['DEPTID_CF', 'SB_APRV_LEVEL'])['CSU_CALSTEDUPERSID'].agg(lambda x: "|".join(map(str, x.unique()))).reset_index()

    for index, row in grouped_df.iterrows():
        # Now for each group, get the business unit, approval level and rule approvers from the row
        sb_aprv_level, csu_calstedupersid, business_unit = row['SB_APRV_LEVEL'], row['CSU_CALSTEDUPERSID'], row['DEPTID_CF']  # assuming 'DEPTID_CF' column holds the business_unit data in your grouped data

    for (sb_aprv_level, csu_calstedupersid, business_unit), group in df.groupby(['SB_APRV_LEVEL', 'CSU_CALSTEDUPERSID', 'BUSINESS_UNIT']):
        modified_bu = modify_business_unit(business_unit)  # Calculate modified_bu here
        deptids = group['DEPTID_CF'].unique().tolist()
        lower_limit, upper_limit = calculate_limits(business_unit, sb_aprv_level)
        document_total = f"Between|{lower_limit}|{upper_limit}|USD"
        rule_group_name = f"DOA Approval: Level {sb_aprv_level}"
        csu_calstedupersid_str = str(csu_calstedupersid)
        if csu_calstedupersid_str.endswith('.0'):
            csu_calstedupersid_str = csu_calstedupersid_str[:-2]
        rule_name = f"DOA RULE: {csu_calstedupersid_str}"
        rule_internal_name = rule_name
        rule_display_name = rule_name
        
       # Check if deptids has more than 49 elements
        if len(deptids) > 49:
            # If deptids has more than 49 elements, split it into chunks of 49
            for i in range(0, len(deptids), 49):
                chunk_deptids = deptids[i:i+49]
                rule_suffix = f":{i//49 + 2:02}"  # Increment the suffix
                rule_internal_name_chunk = f"{rule_internal_name}{rule_suffix}"
                rule_display_name_chunk = f"{rule_display_name}{rule_suffix}"
                deptids_chunk_str = f"DeptID|oneOf|{'|'.join([str(int(val)) + '_' + (replace_text(business_unit).split('|')[1] if len(business_unit.split('|')) > 1 else replace_text(business_unit)) for val in chunk_deptids])}"
                transformed_data.extend([
                    [rule_group_name, rule_group_name, "", rule_internal_name_chunk, rule_display_name_chunk, "", csu_calstedupersid, "", "FALSE", "TRUE", "LineTotal", document_total],
                    [rule_group_name, rule_group_name, "", rule_internal_name_chunk, rule_display_name_chunk, "", csu_calstedupersid, "", "FALSE", "TRUE", "BusinessUnit", modified_bu],
                    [rule_group_name, rule_group_name, "", rule_internal_name_chunk, rule_display_name_chunk, "", csu_calstedupersid, "", "FALSE", "TRUE", "CustomFieldValueMulti", deptids_chunk_str]
                ])

        else:
            # If deptids has 49 or fewer elements, no need to split
            deptids_str = f"DeptID|oneOf|{'|'.join([str(int(val)) + '_' + replace_text(business_unit) for val in deptids])}"
            transformed_data.extend([
                [rule_group_name, rule_group_name, "", rule_internal_name, rule_display_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "LineTotal", document_total],
                [rule_group_name, rule_group_name, "", rule_internal_name, rule_display_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "BusinessUnit", modified_bu],
                [rule_group_name, rule_group_name, "", rule_internal_name, rule_display_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "CustomFieldValueMulti", deptids_str]
            ])

    columns = ["Rule Group Internal Name", "Rule Group Display Name", "Rule Group Description", "Rule Internal Name", "Rule Display Name", "Rule Description", "Rule Approvers", "Implicit Approvers", "Auto Approve", "Active", "Type", "Value"]
    transformed_df = pd.DataFrame(transformed_data, columns=columns)
    transformed_df.to_csv(output_file_path.get(), index=False)

app = tk.Tk()
app.title("DOA App")

frame = ttk.Frame(app, padding=10)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

source_file_path = tk.StringVar()
output_file_path = tk.StringVar()

ttk.Label(frame, text="Select Source CSV File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Button(frame, text="Browse", command=select_source_file).grid(row=0, column=1, padx=5, pady=5)
ttk.Label(frame, textvariable=source_file_path).grid(row=0, column=2, padx=5, pady=5)

ttk.Label(frame, text="Select Output CSV Location:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Button(frame, text="Browse", command=select_output_file).grid(row=1, column=1, padx=5, pady=5)
ttk.Label(frame, textvariable=output_file_path).grid(row=1, column=2, padx=5, pady=5)

ttk.Button(frame, text="Transform Data", command=transform_data).grid(row=2, columnspan=3, pady=10)

app.mainloop()