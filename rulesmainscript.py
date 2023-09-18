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

def transform_data_OLD():
    """Function to process the source file and save the output."""
    # Read the source file ensuring SB_LIMIT_AMT is read as string
    df = pd.read_csv(source_file_path.get(), dtype={'SB_LIMIT_AMT': str})

    # Placeholder for transformed data
    transformed_data = []

    # Group by Rule Group and Rule Name
    for (sb_aprv_level, csu_calstedupersid, business_unit), group in df.groupby(['SB_APRV_LEVEL', 'CSU_CALSTEDUPERSID', 'BUSINESS_UNIT']):

        rule_group_internal_name = f"DOA Approval: Level {sb_aprv_level}"
        rule_group_display_name = f"DOA Approval: Level {sb_aprv_level}"
        rule_group_description = ""  # Add description if needed

        rule_internal_name = f"DOA RULE: {csu_calstedupersid}"
        rule_display_name = f"DOA RULE: {csu_calstedupersid}"
        rule_description = ""  # Add description if needed

        rule_approvers = csu_calstedupersid  # Add approvers if needed
        implicit_approvers = ""  # Add implicit approvers if needed
        auto_approve = "FALSE"  # Set auto approve value if needed
        active = "TRUE"  # Set active value if needed

        # Aggregate department IDs
        deptids = f"DeptID|oneOf|{'|'.join(str(val) for val in group['DEPTID_CF'].unique())}"

        # Handle the spend values stored as text (assuming unique values per group)
        spend_values = str(group['SB_LIMIT_AMT'].iloc[0]).split('-')
        if len(spend_values) == 1:
            lower_limit = 0.01
            upper_limit = float(spend_values[0])
        else:
            lower_limit = float(spend_values[0]) + 0.01
            upper_limit = float(spend_values[1])
        document_total = f"Between|{lower_limit}|{upper_limit}|USD"

        #check for business unit, if it's chico, then the value is CHXCO, if it's FRSNO, then the value is FRXNO, if it's FRATH, then the value is FRXTH.
        if business_unit == "CHICO":
            business_unit = "oneOf|CHXCO"
        elif business_unit == "FRSNO":
            business_unit = "oneOf|FRXNO"
        elif business_unit == "FRATH":
            business_unit = "oneOf|FRXTH"

        # Append to the transformed data
        transformed_data.extend([
            [rule_group_internal_name, rule_group_display_name, rule_group_description, rule_internal_name, rule_display_name, rule_description, rule_approvers, implicit_approvers, auto_approve, active, "DocumentTotal", document_total],
            [rule_group_internal_name, rule_group_display_name, rule_group_description, rule_internal_name, rule_display_name, rule_description, rule_approvers, implicit_approvers, auto_approve, active, "CustomFieldValueMulti", deptids],
            [rule_group_internal_name, rule_group_display_name, rule_group_description, rule_internal_name, rule_display_name, rule_description, rule_approvers, implicit_approvers, auto_approve, active, "BusinessUnit", business_unit]
        ])

    # Create a DataFrame from the transformed data
    output_df = pd.DataFrame(transformed_data, columns=["Rule Group Internal Name", "Rule Group Display Name", "Rule Group Description", "Rule Internal Name", "Rule Display Name", "Rule Description", "Rule Approvers", "Implicit Approvers", "Auto Approve", "Active", "Type", "Value"])

    # Save the transformed data to the output file
    output_df.to_csv(output_file_path.get(), index=False)

    # Update the progress bar
    progress_bar['value'] = 100

def modified_transform_data():
    """Function to process the source file and save the output."""
    # Read the source file ensuring SB_LIMIT_AMT is read as string
    df = pd.read_csv(source_file_path.get(), dtype={'SB_LIMIT_AMT': str})

    # Placeholder for transformed data
    transformed_data = []

    # Group by Rule Group, Rule Name, and Business Unit
    for (sb_aprv_level, csu_calstedupersid, business_unit), group in df.groupby(['SB_APRV_LEVEL', 'CSU_CALSTEDUPERSID', 'BUSINESS_UNIT']):

        rule_group_internal_name = f"DOA Approval: Level {sb_aprv_level}"
        rule_group_display_name = f"DOA Approval: Level {sb_aprv_level}"
        rule_group_description = ""  # Add description if needed

        rule_internal_name = f"DOA RULE: {csu_calstedupersid}"
        rule_display_name = f"DOA RULE: {csu_calstedupersid}"
        rule_description = ""  # Add description if needed

        rule_approvers = csu_calstedupersid  # Add approvers if needed
        implicit_approvers = ""  # Add implicit approvers if needed
        auto_approve = "FALSE"  # Set auto approve value if needed
        active = "TRUE"  # Set active value if needed

        # Aggregate department IDs with business unit suffix
        deptids = f"DeptID|oneOf|{'|'.join([str(val) + '_' + business_unit for val in group['DEPTID_CF'].unique()])}"

        # Handle the spend values stored as text (assuming unique values per group)
        spend_values = str(group['SB_LIMIT_AMT'].iloc[0]).split('-')
        if len(spend_values) == 1:
            lower_limit = 0.01
            upper_limit = float(spend_values[0])
        else:
            lower_limit = float(spend_values[0])
            upper_limit = float(spend_values[1])

        # Create the DocumentTotal value
        document_total = f"Between|{lower_limit}|{upper_limit}|USD"
        
        # Check for business unit, if it's chico, then the value is CHXCO, if it's FRSNO, then the value is FRXNO, if it's FRATH, then the value is FRXTH.
        if business_unit == "CHICO":
            business_unit = "oneOf|CHXCO"
        elif business_unit == "FRSNO":
            business_unit = "oneOf|FRXNO"
        elif business_unit == "FRATH":
            business_unit = "oneOf|FRXTH"

        # Append to the transformed data
        transformed_data.extend([
            [rule_group_internal_name, rule_group_display_name, rule_group_description, rule_internal_name, rule_display_name, rule_description, rule_approvers, implicit_approvers, auto_approve, active, "DocumentTotal", document_total],
            [rule_group_internal_name, rule_group_display_name, rule_group_description, rule_internal_name, rule_display_name, rule_description, rule_approvers, implicit_approvers, auto_approve, active, "CustomFieldValueMulti", deptids],
            [rule_group_internal_name, rule_group_display_name, rule_group_description, rule_internal_name, rule_display_name, rule_description, rule_approvers, implicit_approvers, auto_approve, active, "BusinessUnit", business_unit]
        ])

    # Create a DataFrame from the transformed data
    output_df = pd.DataFrame(transformed_data, columns=["Rule Group Internal Name", "Rule Group Display Name", "Rule Group Description", "Rule Internal Name", "Rule Display Name", "Rule Description", "Rule Approvers", "Implicit Approvers", "Auto Approve", "Active", "Type", "Value"])

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

transform_button = tk.Button(root, text="Transform Data", command=modified_transform_data)
transform_button.pack(pady=20)

progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.pack(pady=20)

root.mainloop()
