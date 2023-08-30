import csv

def convert_approval_rules(input_file, output_file):
    with open(input_file, 'r') as input_csv, open(output_file, 'w', newline='') as output_csv:
        reader = csv.DictReader(input_csv)
        print(reader.fieldnames)
        writer = csv.writer(output_csv)
        
        # Write the header row for the output CSV
        writer.writerow(['Rule Group Internal Name', 'Rule Group Display Name', 'Rule Group Description',
                         'Rule Internal Name', 'Rule Display Name', 'Rule Description', 'Rule Approvers',
                         'Implicit Approvers', 'Auto Approve', 'Active', 'Type', 'Value'])
        
        for row in reader:
            emplid = row['ï»¿EMPLID']
            sb_aprv_level = row['SB_APRV_LEVEL']
            ceptid_cf = row['DEPTID_CF']
            sb_limit_amt = row['SB_LIMIT_AMT']
            
            # Write the CustomFieldValueSingle row
            writer.writerow(['DOA Approval: Level ' + sb_aprv_level, 'DOA Approval: Level ' + sb_aprv_level, '',
                             'DOA RULE: ' + emplid, 'DOA RULE: ' + emplid, '', emplid, '', 'FALSE', 'TRUE',
                             'CustomFieldValueSingle', 'DeptID|equalTo|' + ceptid_cf])
            
            # Write the DocumentTotal row
            writer.writerow(['DOA Approval: Level ' + sb_aprv_level, 'DOA Approval: Level ' + sb_aprv_level, '',
                             'DOA RULE: ' + emplid, 'DOA RULE: ' + emplid, '', emplid, '', 'FALSE', 'TRUE',
                             'DocumentTotal', 'lessThanOrEqualTo|' + sb_limit_amt])

convert_approval_rules('ChicoDOA.csv', 'ApprovalRules.csv')
