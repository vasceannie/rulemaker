import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd

def remove_decimal_point_zero(value):
    if isinstance(value, (float, str)) and str(value).endswith('.0'):
        return str(value)[:-2]
    return value

print(remove_decimal_point_zero(25000000829.0))  # This should print: 25000000829
print(remove_decimal_point_zero("25000000829.0"))  # This should print: 25000000829

def select_source_file():
    path = filedialog.askopenfilename(title="Select Source CSV", filetypes=[("CSV files", "*.csv")])
    source_file_path.set(path)

def select_output_file():
    path = filedialog.asksaveasfilename(title="Select Output CSV Location", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    output_file_path.set(path)

def calculate_limits(business_unit, sb_aprv_level):
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
            3: (0.01, 50000.00)
        }
    }
    return limits.get(business_unit, {}).get(sb_aprv_level, (0, 0))

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

def combine_approvers(df):
    combined_series = df.groupby(['SB_APRV_LEVEL', 'DEPTID_CF'])['CSU_CALSTEDUPERSID'].apply(lambda x: '|'.join(map(lambda y: remove_decimal_point_zero(str(y)), x))).reset_index()
    df = pd.merge(df, combined_series, on=['SB_APRV_LEVEL', 'DEPTID_CF'], suffixes=('', '_combined'))
    df.drop('CSU_CALSTEDUPERSID', axis=1, inplace=True)
    df.rename(columns={'CSU_CALSTEDUPERSID_combined': 'CSU_CALSTEDUPERSID'}, inplace=True)
    return df

def transform_data():
    rule_name_counts = {}
    df = pd.read_csv(source_file_path.get(), dtype={'SB_LIMIT_AMT': str})
    # Debugging line to print unique CSU_CALSTEDUPERSID values
    print("Unique CSU_CALSTEDUPERSID values:", df['CSU_CALSTEDUPERSID'].unique())
    df = combine_approvers(df)
    transformed_data = []

    for (sb_aprv_level, csu_calstedupersid, business_unit), group in df.groupby(['SB_APRV_LEVEL', 'CSU_CALSTEDUPERSID', 'BUSINESS_UNIT']):
        print("Value of csu_calstedupersid:", csu_calstedupersid)  # Existing print line
        print("Data type of csu_calstedupersid:", type(csu_calstedupersid))  # New debugging line
        lower_limit, upper_limit = calculate_limits(business_unit, sb_aprv_level)
        document_total = f"Between|{remove_decimal_point_zero(lower_limit)}|{remove_decimal_point_zero(upper_limit)}|USD"
        modified_bu = modify_business_unit(business_unit)
        deptids = group['DEPTID_CF'].unique()

        for i, chunk_deptids in enumerate([deptids[x:x+49] for x in range(0, len(deptids), 49)]):
            rule_group_name = f"DOA Approval: Level {remove_decimal_point_zero(sb_aprv_level)}"
            rule_suffix = f":{str(i+2).zfill(2)}" if i > 0 else ""
            dept_ids_str = ' '.join(map(remove_decimal_point_zero, deptids))
            base_rule_name = f"{business_unit.replace('[', '').replace(']', '').replace('. ', ' ')} DOA Approval Level {remove_decimal_point_zero(sb_aprv_level)}"
            count = rule_name_counts.get(base_rule_name, 0)
            rule_name_counts[base_rule_name] = count + 1
            if count > 0:
                rule_name = f"{base_rule_name}-{count}"
            else:
                rule_name = base_rule_name
            print(rule_name)  # Let's see the value after transformation

            chunk_deptids = [
                (str(int(remove_decimal_point_zero(val))) if val.replace('.', '', 1).isdigit() else val) + '_' + replace_text(business_unit) 
                for val in chunk_deptids
            ]
            deptids_str = f"DeptID|oneOf|{'|'.join(chunk_deptids)}"
            transformed_data.extend([
                [rule_group_name, rule_group_name, "", rule_name, rule_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "LineTotal", document_total],
                [rule_group_name, rule_group_name, "", rule_name, rule_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "BusinessUnit", modified_bu],
                [rule_group_name, rule_group_name, "", rule_name, rule_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "CustomFieldValueMulti", deptids_str]
            ])

    output_df = pd.DataFrame(transformed_data, columns=["Rule Group Internal Name", "Rule Group Display Name", "Rule Group Description", "Rule Internal Name", "Rule Display Name", "Rule Description", "Rule Approvers", "Implicit Approvers", "Auto Approve", "Active", "Type", "Value"])
    output_df['Value'] = output_df['Value'].apply(replace_text)
    output_df.to_csv(output_file_path.get(), index=False)

app = tk.Tk()
app.title("DOA App")

frame = ttk.Frame(app, padding=10)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

source_file_path = tk.StringVar()
output_file_path = tk.StringVar()

# GUI elements for source file path
ttk.Label(frame, text="Source CSV:").grid(column=0, row=0, sticky=tk.W)
ttk.Entry(frame, width=40, textvariable=source_file_path).grid(column=1, row=0, sticky=(tk.W, tk.E))
ttk.Button(frame, text="Browse", command=select_source_file).grid(column=2, row=0, padx=5)

# GUI elements for output file path
ttk.Label(frame, text="Output CSV:").grid(column=0, row=1, sticky=tk.W)
ttk.Entry(frame, width=40, textvariable=output_file_path).grid(column=1, row=1, sticky=(tk.W, tk.E))
ttk.Button(frame, text="Browse", command=select_output_file).grid(column=2, row=1, padx=5)

# Execute transformation button
ttk.Button(frame, text="Transform Data", command=transform_data).grid(column=1, row=2, pady=10)

app.mainloop()

