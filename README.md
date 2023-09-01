# rulemaker

The code is a Python program that utilizes the Tkinter library to create a GUI application for transforming data from a source CSV file and saving the transformed data into an output CSV file.

The program imports the required packages: tkinter, filedialog, ttk, and pandas.

It defines three functions:
  A. select_source_file(): This function opens a file dialog to allow the user to select the source CSV file. The selected file path is stored in the source_file_path variable.
  B. select_output_file(): This function opens a file dialog to allow the user to select the output CSV file location. The selected file path is stored in the output_file_path variable.
  C. transform_data(): This function processes the data from the source file and saves the transformed data into the output file. It performs the following steps:
    1. Reads the source CSV file using the pandas read_csv() function. It specifies the SB_LIMIT_AMT column to be read as a string.
    2. Defines a placeholder for the transformed data.
    3. Groups the data by the columns SB_APRV_LEVEL, CSU_CALSTEDUPERSID, and BUSINESS_UNIT.
    4. Processes each group and generates the required values for each field.
    5. Appends the transformed data to the placeholder list.
    6. Creates a DataFrame from the transformed data using pandas.
    7. Saves the DataFrame to the output CSV file using the to_csv() function.
    8. Updates the progress bar value to 100.

After defining the functions, the program creates the main application window using tk.Tk(). It sets the title of the window to "ChicoDOA Transformer - CSV".

The program initializes two variables, source_file_path and output_file_path, as tk.StringVar() to store the paths of the selected source and output files.

It creates three UI elements:
  1. source_file_button: A button with the label "Select Source CSV" that when clicked calls the select_source_file() function.
  2. output_file_button: A button with the label "Select Output CSV Location" that when clicked calls the select_output_file() function.
  3. transform_button: A button with the label "Transform Data" that when clicked calls the transform_data() function.

It also creates a progress bar using ttk.Progressbar to indicate the progress of the data transformation.

Finally, the program enters the main event loop using root.mainloop() to start the GUI application.
