# -*- coding: utf-8 -*-
"""
SpectraC 1.0
Created on Thu May 4 00:56:27 2023
@author: Sebastian Mehmed

Description:
    SpectraC is a data filtering and visualization application focused on 
    spectral or chemical data analysis. It offers functionalities like 
    filtering, comparing and plotting.

Note to Readers:
    I know this code is not perfect, and there are areas that could be 
    optimized, such as by the use of "helper functions." This is my first time 
    creating code of this size, and I have worked within certain time 
    constraints. With that said, I am still very happy with the outcome.

    Thank you for reading :)

"""


import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
import os
import glob
import pandas as pd
import numpy as np
import tkinter.font as tkfont
import sv_ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import colors
import matplotlib.ticker as ticker
import csv


class DataFilterApp(tk.Tk):
    
    def __init__(self):
        super().__init__()

        self.title("SpectraC")
        self.state('zoomed')

        self.data_path = tk.StringVar()
        self.all_data = None
        self.displayed_data = None

        self.apply_azure_theme()
        self.create_widgets()
        
        self.relative_intensity = False
        self.common_species_list = False
        self.browse_data = False
        
        self.unique_samples = []
        self.unique_descriptions = []

    def apply_azure_theme(self):
        sv_ttk.set_theme("dark")
        
        # Set up style with and font size
        style = ttk.Style()
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=12)
        style.configure('.', font=default_font)

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
    
        # Create the Treeview widget
        self.treeview = ttk.Treeview(main_frame, height=25)
        self.treeview.grid(row=1, column=0, columnspan=4, padx=(10, 10), pady=(5, 5), sticky="nsew")
    
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL)
        y_scrollbar.grid(row=1, column=4, sticky="ns")
        self.treeview.configure(yscrollcommand=y_scrollbar.set)
        y_scrollbar.config(command=self.treeview.yview)
    
        x_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL)
        x_scrollbar.grid(row=2, column=0, columnspan=4, sticky="ew")
        self.treeview.configure(xscrollcommand=x_scrollbar.set)
        x_scrollbar.config(command=self.treeview.xview)
    
        # Create a frame to hold all the LabelFrames
        container_frame = ttk.Frame(main_frame)
        container_frame.grid(row=0, column=0, sticky="w", padx=(10,0), pady=10)
    
        # Data frame
        data_frame = ttk.LabelFrame(container_frame, text="Data", padding=(5, 5, 5, 5))
        data_frame.grid(row=0, column=0, padx=(0, 10), pady=(5, 5), sticky="w")
    
        folder_label = ttk.Label(data_frame, text="Data folder:")
        folder_label.grid(row=0, column=0, padx=(0, 5), pady=(5, 5), sticky="e")
    
        folder_entry = ttk.Entry(data_frame, textvariable=self.data_path, width=40)
        folder_entry.grid(row=0, column=1, padx=(0, 5), pady=(5, 5))
    
        browse_button = ttk.Button(data_frame, text="Browse", command=self.browse_to_load)
        browse_button.grid(row=0, column=2, padx=(0, 5), pady=(5, 5))
    
        clear_button = ttk.Button(data_frame, text="Clear", command=self.clear_data)
        clear_button.grid(row=0, column=3, padx=(0, 5), pady=(5, 5))
    
        # Search frame
        search_frame = ttk.LabelFrame(container_frame, text="Search", padding=(5, 5, 5, 5))
        search_frame.grid(row=0, column=1, padx=(10, 10), pady=(5,5), sticky="w")
    
        self.search_var = tk.StringVar()
        search_bar = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_bar.grid(row=0, column=0, padx=(0, 5), pady=(5,5))
    
        search_button = ttk.Button(search_frame, text="Search", command=self.search_data)
        search_button.grid(row=0, column=1, padx=(0,5), pady=(5,5))
    
        list_button = ttk.Button(search_frame, text="List", command=self.load_formulas)
        list_button.grid(row=0, column=2, padx=(0, 5), pady=(5, 5))
    
        # Sort frame
        sort_frame = ttk.LabelFrame(container_frame, text="Sorting", padding=(5, 5, 5, 5))
        sort_frame.grid(row=0, column=2, padx=(10, 10), pady=(5, 5), sticky="w")
    
        sort_label = ttk.Label(sort_frame, text="Sort by:")
        sort_label.grid(row=0, column=0, padx=(0, 5), pady=(5, 5), sticky="e")
    
        self.sort_by_var = tk.StringVar()
        sort_options = [
            'C#', 'H#', 'N#', 'O#', 'DBE', 'DBE/C#', 'H/C', 'Sample', 
            'Description', 'Formula', 'Mass', 'Mass (Average)', 
            'Theoretical mass', 'Error', 'Error (Average)', 'Family', 
            'Absolute intensity', 'Absolute intensity (Average)', 
            'Relative intensity', 'Relative intensity (Average)'
            ]
        sort_combobox = ttk.Combobox(sort_frame, textvariable=self.sort_by_var, values=sort_options, width=12)
        sort_combobox.grid(row=0, column=1, padx=(0, 5), pady=(5, 5))
    
        sort_button = ttk.Button(sort_frame, text="Sort", command=lambda: self.sort_data(self.sort_by_var.get()))
        sort_button.grid(row=0, column=2, padx=(0, 5), pady=(5, 5))
    
        # Actions frame
        actions_frame = ttk.LabelFrame(container_frame, text="Actions", padding=(5, 5, 5, 5))
        actions_frame.grid(row=0, column=3, padx=(10, 0), pady=(5, 5), sticky="w")
    
        filter_button = ttk.Button(actions_frame, text="Filter", command=self.open_filter_dialog)
        filter_button.grid(row=0, column=0, padx=(0, 5), pady=(5, 5))
    
        export_button = ttk.Button(actions_frame, text="Export", command=lambda: self.export_data(self.all_data))
        export_button.grid(row=0, column=4, padx=(0, 5), pady=(5, 5))
    
        self.relative_intensity_button = ttk.Button(actions_frame, text="Absolute/Relative", command=self.make_relative_intensity)
        self.relative_intensity_button.grid(row=0, column=1, padx=(0, 5), pady=(5, 5))
    
        comparison_button = ttk.Button(actions_frame, text="Compare", command=self.open_comparison_window)
        comparison_button.grid(row=0, column=2, padx=(0, 5), pady=(5, 5))
    
        plots_button = ttk.Button(actions_frame, text="Plot", command=self.plot_options)
        plots_button.grid(row=0, column=3, padx=(0, 5), pady=(5, 5))
    
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
                
    def browse_to_load(self):
        if self.browse_data:
            messagebox.showerror("Error", "Please clear data first.")
            return
        
        else:
            # If a previous folder path was chosen, start the file explorer from that directory
            initial_dir = getattr(self, 'parent_folder_path', None)
            folder_path = filedialog.askdirectory(initialdir=initial_dir)
    
            if folder_path:
                
                # Save the directory in which the chosen folder resides for next time
                self.parent_folder_path = os.path.dirname(folder_path)
                
                self.data_path.set(folder_path)
                self.load_data(folder_path)
                self.browse_data = True
    
    def load_data(self, folder_path):
        os.chdir(folder_path)
        data_frames = []
    
        for file in glob.glob("*.txt"):
    
            # Load data files
            df = pd.read_csv(file, delimiter=';', header=None, skiprows=2, skipfooter=4, engine='python')
    
            # Set column headers
            df.columns = [
                'Name', 'Formula', 'Mass', 'Theoretical mass', 'Error', 'C#', 
                'H#', 'N#', 'O#', 'DBE', 'DBE/C#', 'H/C', 'Element 1', 
                'Element 2', 'Element 3', 'Element 4', 'Family', 
                'Absolute intensity'
                ]
    
            file_name = os.path.splitext(file)[0]
    
            # Add Columns for "sample" and "description" from the file name
            first_word, second_word = file_name.split('_')
            df['Sample'] = first_word
            df['Description'] = second_word
    
            data_frames.append(df)
    
        # Combine the data into one dataframe
        self.all_data = pd.concat(data_frames, ignore_index=True)
    
        # Remove unwanted columns
        self.all_data = self.all_data.drop(columns=[
            'Name', 'Element 1', 'Element 2', 'Element 3', 'Element 4'
            ])
    
        # Rearrange columns
        self.all_data = self.all_data[[
            'C#', 'H#', 'N#', 'O#', 'DBE', 'DBE/C#', 'H/C', 'Sample', 
            'Description', 'Formula', 'Mass', 'Theoretical mass', 'Error', 
            'Family', 'Absolute intensity'
            ]]
    
        # Strip any extra spaces from the 'Formula' column
        self.all_data['Formula'] = self.all_data['Formula'].str.strip()
    
        # Split the Aromatics family
        self.all_data['DBE/C#'] = self.all_data['DBE/C#'].astype(float)
        self.all_data['Family'] = self.all_data['Family'].str.strip()
    
        aromatics_mask = (self.all_data['Family'] == "Aromatics")
        value_mask = (self.all_data['DBE/C#'] >= 0.67)
    
        # Create new family (Condensed Aromatics)
        combined_mask = np.logical_and(aromatics_mask, value_mask)
        self.all_data.loc[combined_mask, 'Family'] = "Condensed Aromatics"
        
        # Display the data
        self.display_data(self.all_data)
        
    def display_data(self, data):
        self.displayed_data = data
    
        # Clear the treeview before displaying new data
        for row in self.treeview.get_children():
            self.treeview.delete(row)
    
        # Add an empty first column for the Treeview widget
        self.treeview['columns'] = ('',) + tuple(data.columns)
    
        # Configure the first column
        self.treeview.column('', width=0, stretch=tk.NO)
    
        # Update the treeview columns
        padding = 20
        for col in data.columns:
            self.treeview.heading(col, text=col, anchor=tk.W)
    
            # Set the column width based on the maximum width of the content in the column
            max_width = max(tkfont.Font().measure(str(val)) for val in data[col].fillna(''))
            header_width = tkfont.Font().measure(col.title())
            column_width = max(header_width, max_width) + padding
    
            # Use minwidth instead of width to allow resizing
            self.treeview.column(col, anchor=tk.W, minwidth=column_width)
    
        # Add rows to the treeview
        for index, row in data.iterrows():
            self.treeview.insert("", "end", values=(index,) + tuple(row.to_list()))

    def clear_data(self):
        
        # Clear the treeview
        for col in self.treeview["columns"]:
            self.treeview.heading(col, text="")
            self.treeview.column(col, width=0)
            
        self.treeview["columns"] = ()
        
        for row in self.treeview.get_children():
            self.treeview.delete(row)
    
        # Reset variables
        self.data_path.set("")
        self.all_data = None
        self.displayed_data = None
        self.relative_intensity = False
        self.common_species_list = False
        self.browse_data = False
        self.unique_samples = []
        self.unique_descriptions = []
        
    def search_data(self):
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data to search. Please load data first.")
            
        else:
            # Get the search string from the search bar
            search_string = self.search_var.get()
        
            # Split the search string into formulas
            formulas = [formula.strip() for formula in search_string.split(',')]
        
            # Check if there are any formulas to search for
            if not formulas:
                messagebox.showinfo("Info", "No formulas entered. Please enter one or more formulas, separated by commas.")
                return
        
            # Filter the displayed data based on the formulas
            filtered_data = self.displayed_data[self.displayed_data['Formula'].isin(formulas)]
            
            # Check if the filtered data is empty
            if filtered_data.empty:
                messagebox.showinfo("Info", "No data found for the entered formulas. Please check the formulas and try again.")
                
                # Clear the search bar
                self.search_var.set('')
                return
        
            # Update displayed_data with the filtered data
            self.displayed_data = filtered_data
        
            # Redisplay the filtered data
            self.display_data(self.displayed_data)
            
            # Clear the search bar
            self.search_var.set('')

    def load_formulas(self):
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data to search. Please load data first.")
            return
    
        else:
            # Open a file dialog to select the .txt or .csv file
            file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv")])
    
            # Check if a file was selected
            if not file_path:
                messagebox.showinfo("Info", "No file selected. Please select a .txt or .csv file containing the formulas.")
                return
    
            # Load the formulas from the file
            with open(file_path, 'r', encoding='utf-8') as file:
                if file_path.endswith('.csv'):
                    reader = csv.reader(file)
                    formulas = [row[0] for row in reader]
                    # Check for the BOM character and remove it from the first formula if present
                    if formulas and formulas[0].startswith('\ufeff'):
                        formulas[0] = formulas[0][1:]
                else:
                    formulas = [line.strip() for line in file]
                    # Check for the BOM character and remove it from the first formula if present
                    if formulas and formulas[0].startswith('\ufeff'):
                        formulas[0] = formulas[0][1:]
    
            # Update the search bar with the loaded formulas
            self.search_var.set(', '.join(formulas))
    
            # Call search_data method to filter data based on loaded formulas
            self.search_data()
            
    def sort_data(self, column):
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data to sort. Please load data first.")
            return

        else:
            # Sort data by specified column
            sorted_data = self.displayed_data.sort_values(by=column)
            self.display_data(sorted_data)
        
    def filter_data(self, family_filter, c_range, mass_range, intensity_range, c_ranges, mass_ranges):
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            mass = 'Mass'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Relative intensity'
            mass = 'Mass'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            intensity = 'Absolute intensity (Average)'
            mass = 'Mass (Average)'
            
        else:
            intensity = 'Relative intensity (Average)'
            mass = 'Mass (Average)'
        
        # Family filter
        families = [f.strip() for f in family_filter.split(',')]
        filtered_data = self.displayed_data[self.displayed_data['Family'].isin(families)]

        # C# filter
        if c_range:
            c_filter = (filtered_data['C#'] >= c_range[0]) & (filtered_data['C#'] <= c_range[1])
        else:
            c_filter = pd.Series([False] * len(filtered_data), index=filtered_data.index)

        if c_ranges:
            for c_range in c_ranges:
                c_filter |= (filtered_data['C#'] >= c_range[0]) & (filtered_data['C#'] <= c_range[1])

        filtered_data = filtered_data[c_filter]
        
        # Mass filter
        if mass_range:
            mass_filter = (filtered_data[mass] >= mass_range[0]) & (filtered_data[mass] <= mass_range[1])
        else:
            mass_filter = pd.Series([False] * len(filtered_data), index=filtered_data.index)

        if mass_ranges:
            for mass_range in mass_ranges:
                mass_filter |= (filtered_data[mass] >= mass_range[0]) & (filtered_data[mass] <= mass_range[1])

        filtered_data = filtered_data[mass_filter]
        
        # Absolute/Relative intensity filter
        filtered_data = filtered_data[(filtered_data[intensity] >= intensity_range[0]) & (filtered_data[intensity] <= intensity_range[1])]
        self.display_data(filtered_data)
    
    def open_filter_dialog(self):
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data to filter. Please load data first.")
            return
        
        elif self.common_species_list == True:
            messagebox.showerror("Error", "Not possible with common species list.")
            return
            
        else:
            FilterDialog(self, self.displayed_data, self.filter_data)
            
    def make_relative_intensity(self):
        
        def calculate_relative_intensity(group):
            max_value = group.max()
            return group / max_value * 100
        
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data, Please load data first.")
            return
            
        elif not ('Sample' in self.displayed_data) or not ('Description' in self.displayed_data):
            messagebox.showerror("Error", "Not possible after compare")
            return
            
        else:    
            # Create the dictionary to hold the original values
            if not hasattr(self, 'abs_intensity_dict'):
                self.abs_intensity_dict = self.displayed_data.set_index(['Sample', 'Description', 'Formula'])['Absolute intensity'].to_dict()
            
            # Calculate the relative intensity
            if not self.relative_intensity:
                self.displayed_data['Relative intensity'] = self.displayed_data.groupby(['Sample', 'Description'])['Absolute intensity'].transform(calculate_relative_intensity)
                self.displayed_data.drop('Absolute intensity', axis=1, inplace=True)
                self.relative_intensity = True
                    
            else:
                # Retrieve the original absolute intensity values from the dictionary
                self.displayed_data['Absolute intensity'] = self.displayed_data.apply(lambda row: self.abs_intensity_dict[(row['Sample'], row['Description'], row['Formula'])], axis=1)
                self.displayed_data.drop('Relative intensity', axis=1, inplace=True)
                self.relative_intensity = False
            
            self.display_data(self.displayed_data)
            
    def open_comparison_window(self):
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data to compare. Please load data first")
            return
        
        elif not ('Sample' in self.displayed_data) or not ('Description' in self.displayed_data):
            messagebox.showerror("Error", "Not possible to compare twice, please clear and reload the data.")
            return
            
        else:
            def make_average_and_close():
                self.make_average()
                comparison_window.destroy()
            
            def find_similarities_and_close():
                self.find_common_species()
                comparison_window.destroy()
                
            # def find_differences_and_close():
            #     self.find_differences()
            #     comparison_window.destroy()
        
            # Create new window
            comparison_window = tk.Toplevel(self.master)
            comparison_window.title("Comparison")
            comparison_window.geometry("500x500")
        
            # Center the window relative to the main window
            main_window = self.winfo_toplevel()
            main_window_x = main_window.winfo_x()
            main_window_y = main_window.winfo_y()
            main_window_width = main_window.winfo_width()
            main_window_height = main_window.winfo_height()
        
            comparison_window_x = main_window_x + (main_window_width // 2) - (500 // 2)
            comparison_window_y = main_window_y + (main_window_height // 2) - (500 // 2)
        
            comparison_window.geometry(f"+{comparison_window_x}+{comparison_window_y}")
        
            # Create a frame inside the comparison window to hold the buttons
            button_frame = ttk.Frame(comparison_window)
            button_frame.pack(side='left', expand=True)
        
            # Create a frame to hold the sample check buttons
            sample_frame_container = ttk.Frame(comparison_window)
            sample_frame_container.pack(side='right', fill='both', expand=True)
        
            sample_frame = ttk.Frame(sample_frame_container)
            sample_frame.pack(expand=True, anchor='center')
        
            # Get unique combinations of 'Sample' and 'Description'
            samples = self.displayed_data[['Sample', 'Description']].drop_duplicates().apply(lambda x: f"{x[0]} - {x[1]}", axis=1)
        
            # Create a dictionary to hold the sample selection variables
            self.sample_vars = {sample: tk.BooleanVar() for sample in samples}
        
            # Create a check button for each unique sample
            for i, sample in enumerate(samples):
                ttk.Checkbutton(sample_frame, text=sample, variable=self.sample_vars[sample]).pack(anchor='w')
        
            make_average_button = ttk.Button(button_frame, text="Average", command=make_average_and_close)
            make_average_button.grid(row=0, column=0, padx=(0, 5), pady=(5, 5))
        
            find_similarities_button = ttk.Button(button_frame, text="Common Species", command=find_similarities_and_close)
            find_similarities_button.grid(row=1, column=0, padx=5, pady=5)
        
            # find_differences_button = ttk.Button(button_frame, text="Find Differences", command=find_differences_and_close)
            # find_differences_button.grid(row=2, column=0, padx=5, pady=5)
        
            # Center the buttons in the button_frame
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_rowconfigure(0, weight=1)
            button_frame.grid_rowconfigure(1, weight=1)
            button_frame.grid_rowconfigure(2, weight=1)

    def make_average(self):
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
    
        else:
            intensity = 'Relative intensity'
    
        # Filter data based on the samples selected by the user
        selected_samples = [sample for sample, var in self.sample_vars.items() if var.get()]
        
        if not selected_samples:
            messagebox.showerror("Error", "No samples selected. Please select at least one sample.")
            return
    
        # Convert each selected sample back into its 'Sample' and 'Description' parts
        selected_samples = [sample.split(" - ") for sample in selected_samples]
        number_selected_samples = len(selected_samples)
        
        # Extract samples and descriptions from selected_samples to be used later
        self.unique_samples, self.unique_descriptions = zip(*selected_samples)
    
        # Filter 'displayed_data' to include only the selected samples
        self.displayed_data = self.displayed_data[self.displayed_data.apply(
            lambda row: [row['Sample'], row['Description']] in selected_samples, axis=1)]
    
        # Calculate the average of the selected samples
        unique_formulas = self.displayed_data['Formula'].unique()
        unique_combinations = self.displayed_data.drop_duplicates(subset=['Sample', 'Description'])
        columns_to_keep = ['C#', 'H#', 'N#', 'O#', 'DBE', 'DBE/C#', 'H/C', 'Formula', 'Mass', 'Theoretical mass', 'Error', 'Family']
        averaged_data = []
    
        for formula in unique_formulas:
            formula_data = self.displayed_data[self.displayed_data['Formula'] == formula]
            representative_rows = []
    
            for _, combination in unique_combinations.iterrows():
                temp_data = formula_data[(formula_data['Sample'] == combination['Sample']) & (formula_data['Description'] == combination['Description'])]
                
                if not temp_data.empty:
                    min_error_row = temp_data.loc[temp_data['Error'].abs().idxmin()]
                    representative_rows.append(min_error_row)
    
            if len(representative_rows) > 0:
                representative_row = pd.concat(representative_rows, axis=1).mean(axis=1, numeric_only=True).to_frame().T
                representative_row = representative_row.drop(columns=['Sample', 'Description', intensity])
                representative_row[columns_to_keep] = representative_rows[0].loc[columns_to_keep]
                representative_row['Mass'] = sum([row['Mass'] for row in representative_rows]) / len(formula_data)
                representative_row['Error'] = sum([row['Error'] for row in representative_rows]) / len(formula_data)
    
                for row in representative_rows:
                    combination = row['Sample'] + '_' + row['Description']
                    
                    if intensity == 'Absolute intensity':
                        representative_row['Absolute intensity (' + combination + ')'] = row[intensity]
                        
                    else:
                        representative_row['Relative intensity (' + combination + ')'] = row[intensity]
    
                averaged_data.append(representative_row)
    
        df_averaged = pd.DataFrame(pd.concat(averaged_data, ignore_index=True))
        
        if intensity == 'Absolute intensity':
            df_averaged['Absolute intensity (Average)'] = df_averaged.filter(regex='^Absolute intensity \(').sum(axis=1) / number_selected_samples
            
        else:
            df_averaged['Relative intensity (Average)'] = df_averaged.filter(regex='^Relative intensity \(').sum(axis=1) / number_selected_samples
    
        # Replace all 'nan' values with 0
        # We get 'nan' values when a sample does not contain the 'Formula'
        # Which mean the intensity is 0
        df_averaged.fillna(0, inplace=True)
    
        # Rename 'Mass' and 'Error' to 'Mass (Average)' and 'Error (Average)'
        df_averaged = df_averaged.rename(columns={'Mass': 'Mass (Average)', 'Error': 'Error (Average)'})
    
        # Display averaged data
        self.display_data(df_averaged)
            
    def find_common_species(self):
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data to compare. Please load data first.")
            return
        
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            
        else:
            intensity = 'Relative intensity'
    
        # Filter data based on the samples selected by the user
        selected_samples = [sample for sample, var in self.sample_vars.items() if var.get()]
        
        if not selected_samples:
            messagebox.showerror("Error", "No samples selected. Please select at least one sample.")
            return
    
        # Convert each selected sample back into its 'Sample' and 'Description' parts
        selected_samples = [sample.split(" - ") for sample in selected_samples]
        number_selected_samples = len(selected_samples)
        
        # Extract samples and descriptions from selected_samples to be used later
        self.unique_samples, self.unique_descriptions = zip(*selected_samples)
        
        # Filter 'displayed_data' to include only the selected samples
        self.displayed_data = self.displayed_data[self.displayed_data.apply(lambda row: [row['Sample'], row['Description']] in selected_samples, axis=1)]
    
        # Group data by 'Sample' and 'Description' and extract unique 'Formula' for each group
        grouped_data = self.displayed_data.groupby(['Sample', 'Description'])['Formula'].unique()
    
        # Find common 'Formula' across all groups
        common_species = set(grouped_data[0])
        
        for species in grouped_data[1:]:
            common_species.intersection_update(species)
    
        columns_to_keep = [
            'C#', 'H#', 'N#', 'O#', 'DBE', 'DBE/C#', 'H/C', 'Formula', 'Mass', 
            'Theoretical mass', 'Error', 'Family'
            ]
        averaged_data = []
        
        for formula in common_species:
            formula_data = self.displayed_data[self.displayed_data['Formula'] == formula]
            representative_rows = []
        
            for combination in grouped_data.index:
                temp_data = formula_data[(formula_data['Sample'] == combination[0]) & (formula_data['Description'] == combination[1])]
                if not temp_data.empty:
                    min_error_row = temp_data.loc[temp_data['Error'].abs().idxmin()]  # Find the row with the error closest to 0
                    representative_rows.append(min_error_row)
    
            if len(representative_rows) > 0:
                representative_row = pd.concat(representative_rows, axis=1).mean(axis=1, numeric_only=True).to_frame().T
                representative_row = representative_row.drop(columns=['Sample', 'Description', intensity])
                representative_row[columns_to_keep] = representative_rows[0].loc[columns_to_keep]  # Keep only the desired columns
                representative_row['Mass'] = sum([row['Mass'] for row in representative_rows]) / len(formula_data)  # New average Mass calculation
                representative_row['Error'] = sum([row['Error'] for row in representative_rows]) / len(formula_data)  # New average Error calculation
    
                for row in representative_rows:
                    combination = row['Sample'] + '_' + row['Description']
                    if intensity == 'Absolute intensity':
                        representative_row['Absolute intensity (' + combination + ')'] = row[intensity]
                    else:
                        representative_row['Relative intensity (' + combination + ')'] = row[intensity]
    
                averaged_data.append(representative_row)
    
        df_common_species = pd.DataFrame(pd.concat(averaged_data, ignore_index=True))
    
        # Rename 'Mass' and 'Error' to 'Mass (Average)' and 'Error (Average)'
        df_common_species = df_common_species.rename(columns={'Mass': 'Mass (Average)', 'Error': 'Error (Average)'})
        
        # Add a new column for the average intensity
        if intensity == 'Absolute intensity':
            intensity_columns = df_common_species.filter(regex='^Absolute intensity \(').columns
            df_common_species[intensity + ' (Average)'] = df_common_species[intensity_columns].sum(axis=1) / number_selected_samples

        else:
            intensity_columns = df_common_species.filter(regex='^Relative intensity \(').columns
            df_common_species[intensity + ' (Average)'] = df_common_species[intensity_columns].sum(axis=1) / number_selected_samples
        
        self.common_species_list = True
        self.display_data(df_common_species)
            
    def plot_options(self):
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data to plot. Please load data first.")
            return
        
        else:
            def make_plot_and_destroy(x, y):
                self.plot_option = f"{y} vs {x}"
                self.x_col_for_grouped_plot = x
                self.y_col_for_grouped_plot = y
                self.group_selection_window()
                top.destroy()
        
            def make_ai_plots_and_destroy():
                self.plot_option = "AI vs C#"
                self.group_selection_window()
                top.destroy()
                
            def open_group_selection_and_destroy():
                self.plot_option = "Common Species"
                selected_samples = [sample for sample, var in self.sample_vars.items() if var.get()]
                if len(selected_samples) > 2:
                    messagebox.showerror("Error", "Maximum 2 samples can be selected for Common Species plot.")
                    return
                
                elif 'Absolute intensity (Average)' in self.displayed_data:
                    messagebox.showerror("Error", "Not possible with average data")
                    return
                
                else:
                    self.group_selection_window()
                    top.destroy()
                    
            def open_family_selection_and_destroy():
                self.plot_option = "Family Analysis"
                self.family_selection_window()
                top.destroy()
            
            # Define the different plot combinations
            plot_combinations = [
                ('C#', 'DBE'),
                ('C#', 'H#'),
                ('Mass', 'H/C'),
                ('C#', 'AI'),
                ('Family Analysis', ''),
                ('Common Species', '')
            ]
        
            # Create new window
            top = tk.Toplevel()
            top.title("Choose plot and samples")
        
            # Set the size of the new window
            top.geometry("500x500")
        
            # Center the window relative to the main window
            main_window = self.winfo_toplevel()
            main_window_x = main_window.winfo_x()
            main_window_y = main_window.winfo_y()
            main_window_width = main_window.winfo_width()
            main_window_height = main_window.winfo_height()
        
            comparison_window_x = main_window_x + (main_window_width // 2) - (500 // 2)
            comparison_window_y = main_window_y + (main_window_height // 2) - (500 // 2)
        
            top.geometry(f"+{comparison_window_x}+{comparison_window_y}")
        
            # Create a frame inside the comparison window to hold the buttons
            button_frame = ttk.Frame(top)
            button_frame.pack(side='left', expand=True)
        
            # Create a frame to hold the sample check buttons
            sample_frame_container = ttk.Frame(top)
            sample_frame_container.pack(side='right', fill='both', expand=True)
        
            sample_frame = ttk.Frame(sample_frame_container)
            sample_frame.pack(expand=True, anchor='center')
            
            if 'Sample' and 'Description' in self.displayed_data:
                
                # Get unique combinations of 'Sample' and 'Description'
                samples = self.displayed_data[['Sample', 'Description']].drop_duplicates().apply(lambda x: f"{x[0]} - {x[1]}", axis=1)
            
                # Create a dictionary to hold the sample selection variables
                self.sample_vars = {sample: tk.BooleanVar() for sample in samples}
            
                # Create a check button for each unique sample
                for i, sample in enumerate(samples):
                    ttk.Checkbutton(sample_frame, text=sample, variable=self.sample_vars[sample]).pack(anchor='w')
        
            # Create the buttons for the different plot options
            for i, (x_col, y_col) in enumerate(plot_combinations):
                if y_col == 'AI' and x_col == 'C#':
                    button = ttk.Button(button_frame, text=f"{y_col} vs {x_col}", 
                                        command=make_ai_plots_and_destroy)
        
                elif y_col == '' and x_col == 'Family Analysis':
                    button = ttk.Button(button_frame, text=f"{x_col}", 
                                        command=open_family_selection_and_destroy)
                    
                elif y_col == '' and x_col == 'Common Species':
                    button = ttk.Button(button_frame, text=f"{x_col}", 
                                        command=open_group_selection_and_destroy)
        
                else:
                    button = ttk.Button(button_frame, text=f"{y_col} vs {x_col}", 
                                        command=lambda x=x_col, y=y_col: make_plot_and_destroy(x, y))
        
                button.grid(row=i, column=0, padx=5, pady=5)
        
                # Center the buttons in the button_frame
                button_frame.grid_columnconfigure(0, weight=1)
                
                for j in range(len(plot_combinations)):
                    button_frame.grid_rowconfigure(j, weight=1)
            
    def group_selection_window(self):
        
        def destroy_and_select_asymptote():
            family_selection_window.destroy()
            self.asymptote_selection_window()
            
        def destroy_and_scale():
            family_selection_window.destroy()
            self.axis_scale_window()
            
        # Create new window
        family_selection_window = tk.Toplevel()
        family_selection_window.title("Select Groups")

        # Center the window relative to the main window
        main_window = self.winfo_toplevel()
        main_window_x = main_window.winfo_x()
        main_window_y = main_window.winfo_y()
        main_window_width = main_window.winfo_width()
        main_window_height = main_window.winfo_height()

        comparison_window_x = main_window_x + (main_window_width // 2) - (300 // 2)
        comparison_window_y = main_window_y + (main_window_height // 2) - (200 // 2)

        family_selection_window.geometry(f"+{comparison_window_x}+{comparison_window_y}")

        # Define the group names
        group_names = ["CH Species", "CHN Species", "CHO Species", "CHNO Species"]

        # Create a dictionary to hold the group selection variables
        self.group_vars = {group: tk.BooleanVar() for group in group_names}

        for i, group in enumerate(group_names):
            # Create a checkbutton for each group
            ttk.Checkbutton(family_selection_window, text=group, variable=self.group_vars[group]).grid(row=i, column=0, sticky='w')

        # Add a "Next" button at the bottom of the window
        if self.plot_option in ["DBE vs C#", "AI vs C#", "H# vs C#"]:
            next_button = ttk.Button(family_selection_window, text="Next", command=destroy_and_select_asymptote)
            
        else:
            next_button = ttk.Button(family_selection_window, text="Next", command=destroy_and_scale)
            
        next_button.grid(row=i+1, column=0)
        
    def asymptote_selection_window(self):
        
        def destroy_and_scale():
            asymptote_selection_window.destroy()
            self.axis_scale_window()
        
        # Create new window
        asymptote_selection_window = tk.Toplevel()
        asymptote_selection_window.title("Select Asymptotes")
    
        # Center the window relative to the main window
        main_window = self.winfo_toplevel()
        main_window_x = main_window.winfo_x()
        main_window_y = main_window.winfo_y()
        main_window_width = main_window.winfo_width()
        main_window_height = main_window.winfo_height()
    
        asymptote_window_x = main_window_x + (main_window_width // 2) - (300 // 2)
        asymptote_window_y = main_window_y + (main_window_height // 2) - (200 // 2)
    
        asymptote_selection_window.geometry(f"+{asymptote_window_x}+{asymptote_window_y}")
    
        # Define the asymptote names
        if self.plot_option == "DBE vs C#":
            asymptote_names = [
                "DBE = 0.5*C# (Aromatic)", 
                "DBE = 0.67*C# (Condensed Aromatic)",
                "DBE = 0.735*C# - 0.5 (Cata-condensed PAHs)",
                "DBE = 0.92*C# - 3.24 (Peri-condensed PAHs)",
                "DBE = 0.9*C# (HC Cluster)", 
                "DBE = C#+1 (Carbon Clusters)"
                ]
        
        elif self.plot_option == "AI vs C#":
            asymptote_names = [
                "AI = 0.5 (Aromatic)", 
                "AI = 0.67 (Condensed Aromatic)",
                "AI = 0.735 - 0.5/C# (Cata-condensed PAHs)",
                "AI = 0.92 - 3.24/C# (Peri-condensed PAHs)",
                "AI = 0.9 (HC Cluster)", 
                "AI = 1 + 1/C# (Carbon Clusters)"
                ]
            
        elif self.plot_option == "H# vs C#":
            asymptote_names = [
                "H# = sqrt(6*C#) (Peri-condensed PAHs)", 
                "H# = 0.5*C# + 3 (Cata-condensed PAHs)", 
                "H# = C#", 
                "H# = 1.25*C# + 2.5 (Aliphatic/Aromatic)",
                "H# = 2*C# + 2 (Aliphatic)"
                ]
    
        # Create a dictionary to hold the asymptote selection variables
        self.asymptote_vars = {asymptote: tk.BooleanVar() for asymptote in asymptote_names}
    
        for i, asymptote in enumerate(asymptote_names):
            # Create a checkbutton for each asymptote
            ttk.Checkbutton(asymptote_selection_window, text=asymptote, variable=self.asymptote_vars[asymptote]).grid(row=i, column=0, sticky='w')
    
        # Add a "Next" button at the bottom of the window
        next_button = ttk.Button(asymptote_selection_window, text="Next", command=destroy_and_scale)
        next_button.grid(row=i+1, column=0)
        
    def axis_scale_window(self):
        
        def destroy_and_plot():
            # Destroy the scale window and proceed to plotting
            scale_window.destroy()
            self.plot_selected_groups()
            
        if 'Sample' and 'Description' in self.displayed_data:
            
            # Get 'Sample' and 'Description' from selected samples
            selected_samples_descriptions = [(sample.split(" - ")[0], sample.split(" - ")[1]) for sample, var in self.sample_vars.items() if var.get()]
            
            # Get maximum values from selected samples
            C_num_max_val = self.displayed_data[(self.displayed_data['Sample'].isin([sd[0] for sd in selected_samples_descriptions])) &
                                                (self.displayed_data['Description'].isin([sd[1] for sd in selected_samples_descriptions]))]['C#'].max()
            
            DBE_max_val = self.displayed_data[(self.displayed_data['Sample'].isin([sd[0] for sd in selected_samples_descriptions])) &
                                                (self.displayed_data['Description'].isin([sd[1] for sd in selected_samples_descriptions]))]['DBE'].max()
            
            H_num_max_val = self.displayed_data[(self.displayed_data['Sample'].isin([sd[0] for sd in selected_samples_descriptions])) &
                                                (self.displayed_data['Description'].isin([sd[1] for sd in selected_samples_descriptions]))]['H#'].max()
            
            H_C_ratio_max_val = self.displayed_data[(self.displayed_data['Sample'].isin([sd[0] for sd in selected_samples_descriptions])) &
                                                (self.displayed_data['Description'].isin([sd[1] for sd in selected_samples_descriptions]))]['H/C'].max()
            
            Mass_max_val = self.displayed_data[(self.displayed_data['Sample'].isin([sd[0] for sd in selected_samples_descriptions])) &
                                                (self.displayed_data['Description'].isin([sd[1] for sd in selected_samples_descriptions]))]['Mass'].max()
            
        else:
            C_num_max_val = self.displayed_data['C#'].max()
            DBE_max_val = self.displayed_data['DBE'].max()
            H_num_max_val = self.displayed_data['H#'].max()
            H_C_ratio_max_val = self.displayed_data['H/C'].max()
            Mass_max_val = self.displayed_data['Mass (Average)'].max()

        # Create new window
        scale_window = tk.Toplevel()
        scale_window.title("Set Axis Scales")
        
        # Center the window relative to the main window
        main_window = self.winfo_toplevel()
        main_window_x = main_window.winfo_x()
        main_window_y = main_window.winfo_y()
        main_window_width = main_window.winfo_width()
        main_window_height = main_window.winfo_height()

        comparison_window_x = main_window_x + (main_window_width // 2) - (300 // 2)
        comparison_window_y = main_window_y + (main_window_height // 2) - (200 // 2)
        
        scale_window.geometry(f"+{comparison_window_x}+{comparison_window_y}")
        
        if self.plot_option == "AI vs C#":
            # Axis scale variables
            self.AI_min = tk.DoubleVar(value=0)
            self.AI_max = tk.DoubleVar(value=1.3)
            self.C_num_min = tk.DoubleVar(value=0)
            self.C_num_max = tk.DoubleVar(value=C_num_max_val)
        
            # Create entries for each axis scale variable
            ttk.Label(scale_window, text="AI Min:").grid(row=0, column=0)
            ttk.Entry(scale_window, textvariable=self.AI_min).grid(row=0, column=1)
        
            ttk.Label(scale_window, text="AI Max:").grid(row=1, column=0)
            ttk.Entry(scale_window, textvariable=self.AI_max).grid(row=1, column=1)
        
            ttk.Label(scale_window, text="C# Min:").grid(row=2, column=0)
            ttk.Entry(scale_window, textvariable=self.C_num_min).grid(row=2, column=1)
        
            ttk.Label(scale_window, text="C# Max:").grid(row=3, column=0)
            ttk.Entry(scale_window, textvariable=self.C_num_max).grid(row=3, column=1)
    
        elif self.plot_option == "DBE vs C#" or self.plot_option == "Common Species":
            # Axis scale variables
            self.DBE_min = tk.DoubleVar(value=0)
            self.DBE_max = tk.DoubleVar(value=DBE_max_val)
            self.C_num_min = tk.DoubleVar(value=0)
            self.C_num_max = tk.DoubleVar(value=C_num_max_val)
        
            # Create entries for each axis scale variable
            ttk.Label(scale_window, text="DBE Min:").grid(row=0, column=0)
            ttk.Entry(scale_window, textvariable=self.DBE_min).grid(row=0, column=1)
        
            ttk.Label(scale_window, text="DBE Max:").grid(row=1, column=0)
            ttk.Entry(scale_window, textvariable=self.DBE_max).grid(row=1, column=1)
        
            ttk.Label(scale_window, text="C# Min:").grid(row=2, column=0)
            ttk.Entry(scale_window, textvariable=self.C_num_min).grid(row=2, column=1)
        
            ttk.Label(scale_window, text="C# Max:").grid(row=3, column=0)
            ttk.Entry(scale_window, textvariable=self.C_num_max).grid(row=3, column=1)
            
        elif self.plot_option == "H# vs C#":
            # Axis scale variables
            self.H_num_min = tk.DoubleVar(value=0)
            self.H_num_max = tk.DoubleVar(value=H_num_max_val)  # Define H_num_max_val elsewhere
            self.C_num_min = tk.DoubleVar(value=0)
            self.C_num_max = tk.DoubleVar(value=C_num_max_val)
        
            # Create entries for each axis scale variable
            ttk.Label(scale_window, text="H# Min:").grid(row=0, column=0)
            ttk.Entry(scale_window, textvariable=self.H_num_min).grid(row=0, column=1)
        
            ttk.Label(scale_window, text="H# Max:").grid(row=1, column=0)
            ttk.Entry(scale_window, textvariable=self.H_num_max).grid(row=1, column=1)
        
            ttk.Label(scale_window, text="C# Min:").grid(row=2, column=0)
            ttk.Entry(scale_window, textvariable=self.C_num_min).grid(row=2, column=1)
        
            ttk.Label(scale_window, text="C# Max:").grid(row=3, column=0)
            ttk.Entry(scale_window, textvariable=self.C_num_max).grid(row=3, column=1)
            
        elif self.plot_option == "H/C vs Mass":
            # Axis scale variables
            self.HC_min = tk.DoubleVar(value=0)
            self.HC_max = tk.DoubleVar(value=H_C_ratio_max_val)  # Define H_C_ratio_max_val elsewhere
            self.Mass_min = tk.DoubleVar(value=0)
            self.Mass_max = tk.DoubleVar(value=Mass_max_val)  # Define Mass_max_val elsewhere
        
            # Create entries for each axis scale variable
            ttk.Label(scale_window, text="H/C Min:").grid(row=0, column=0)
            ttk.Entry(scale_window, textvariable=self.HC_min).grid(row=0, column=1)
        
            ttk.Label(scale_window, text="H/C Max:").grid(row=1, column=0)
            ttk.Entry(scale_window, textvariable=self.HC_max).grid(row=1, column=1)
        
            ttk.Label(scale_window, text="Mass Min:").grid(row=2, column=0)
            ttk.Entry(scale_window, textvariable=self.Mass_min).grid(row=2, column=1)
        
            ttk.Label(scale_window, text="Mass Max:").grid(row=3, column=0)
            ttk.Entry(scale_window, textvariable=self.Mass_max).grid(row=3, column=1)
            
        # Axis scale variables for color intensity
        self.intensity_min = tk.DoubleVar(value=0)
        self.intensity_max = tk.DoubleVar(value=0)
        
        # Create entries for color intensity scale variables
        ttk.Label(scale_window, text="Intensity Min:").grid(row=4, column=0)
        ttk.Entry(scale_window, textvariable=self.intensity_min).grid(row=4, column=1)
        
        ttk.Label(scale_window, text="Intensity Max:").grid(row=5, column=0)
        ttk.Entry(scale_window, textvariable=self.intensity_max).grid(row=5, column=1)
        
        # Add a plot button at the bottom of the window
        plot_button = ttk.Button(scale_window, text="Plot", command=destroy_and_plot)
        plot_button.grid(row=6, column=0, columnspan=2)
        
    def plot_selected_groups(self):
        # Get the selected groups
        selected_groups = [group for group, var in self.group_vars.items() if var.get()]
    
        # Call the appropriate plot method
        if self.plot_option == "Common Species":
            self.plot_common_species(selected_groups)
            
        elif self.plot_option == "AI vs C#":
            self.make_ai_plots(selected_groups)
            
        else:
            self.make_plot(self.x_col_for_grouped_plot, self.y_col_for_grouped_plot)
        
    def create_group_column(self):
        # Define the group conditions
        conditions = [
            self.displayed_data['Family'].isin(['Aliphatics', 'Aromatics', 'Condensed Aromatics', 'HC Clusters', 'Carbon Clusters', 'Fullerenes']),
            self.displayed_data['Family'] == 'Nitrogen Species',
            self.displayed_data['Family'] == 'Oxygen Species',
            self.displayed_data['Family'] == 'Nitrogen Oxygen Species'
        ]
        
        # Define the group names
        group_names = ["CH Species", "CHN Species", "CHO Species", "CHNO Species"]
        
        # Apply the conditions and create a new 'Group' column
        self.displayed_data['Group'] = np.select(conditions, group_names)

    def make_plot(self, x_col, y_col):
        
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Relative intensity'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            intensity = 'Absolute intensity (Average)'
            
        else:
            intensity = 'Relative intensity (Average)'
            
        # Get the min and max intensity values from the user input
        intensity_min = self.intensity_min.get()
        intensity_max = self.intensity_max.get()
        
        # Create a custom logarithmic colormap normalization with the defined min and max values if they are set
        if intensity_min == 0.0 and intensity_max == 0.0:
            # default logarithmic scaling without custom min and max values
            custom_norm = colors.LogNorm()
              
        else:
            if intensity_min == 0.0 or intensity_max == 0.0:
                messagebox.showerror("Error", "The logarithm of 0 is not defined. Please enter another value")
            else:
                custom_norm = colors.LogNorm(vmin=intensity_min, vmax=intensity_max, clip=True)
            
        asymptote_colors = {
            "DBE = 0.5*C# (Aromatic)": 'red',
            "DBE = 0.67*C# (Condensed Aromatic)": 'blue',
            "DBE = 0.735*C# - 0.5 (Cata-condensed PAHs)": 'green',
            "DBE = 0.92*C# - 3.24 (Peri-condensed PAHs)": 'purple',
            "DBE = 0.9*C# (HC Cluster)": 'orange',
            "DBE = C#+1 (Carbon Clusters)": 'brown',
            "H# = sqrt(6*C#) (Peri-condensed PAHs)": 'purple',
            "H# = 0.5*C# + 3 (Cata-condensed PAHs)": 'green',
            "H# = C#": 'cyan',
            "H# = 1.25*C# + 2.5 (Aliphatic/Aromatic)": 'magenta',
            "H# = 2*C# + 2 (Aliphatic)": 'yellow'
        }

        # Call the method to create the 'Group' column
        self.create_group_column()  

        if 'Sample' and 'Description' in self.displayed_data:
            has_sample_description = 'Sample' in self.displayed_data.columns and 'Description' in self.displayed_data.columns
            has_group = 'Group' in self.displayed_data.columns
    
            if has_sample_description and has_group:
                
                # Group the data by 'Sample', 'Description', and 'Group'
                grouped_data = self.displayed_data.groupby(['Sample', 'Description', 'Group'])
                
                for (sample, description, group), group_data in grouped_data:
                    
                    # Check if the sample and the group are selected to be plotted
                    if self.sample_vars.get(f"{sample} - {description}", tk.BooleanVar(value=False)).get() and self.group_vars.get(group, tk.BooleanVar(value=False)).get():
                        fig, ax = plt.subplots()
                        sc = ax.scatter(group_data[x_col], group_data[y_col], c=group_data[intensity], cmap='viridis', marker='.', norm=custom_norm)
                        ax.set_xlabel(x_col)
                        ax.set_ylabel(y_col)
                        
                        if self.plot_option == "DBE vs C#":
                            
                            # Set the axis limits based on the variables from the scale window
                            ax.set_xlim(self.C_num_min.get(), self.C_num_max.get())
                            ax.set_ylim(self.DBE_min.get(), self.DBE_max.get())
        
                            # Define the asymptote details
                            asymptote_details = [
                                (0.5, 6, "DBE = 0.5*C# (Aromatic)"),
                                (0.67, 10, "DBE = 0.67*C# (Condensed Aromatic)"),
                                (0.735, 10, "DBE = 0.735*C# - 0.5 (Cata-condensed PAHs)"),
                                (0.92, 16, "DBE = 0.92*C# - 3.24 (Peri-condensed PAHs)"),
                                (0.9, 6, "DBE = 0.9*C# (HC Cluster)"),
                                (None, 2, "DBE = C#+1 (Carbon Clusters)")
                            ]
        
                            # Check if the asymptote is selected to be plotted
                            for asymptote_value, start_point, asymptote in asymptote_details:
                                if self.asymptote_vars.get(asymptote).get():
                                    x_values = np.linspace(start_point, ax.get_xlim()[1], 100)
                                    color = asymptote_colors[asymptote]
        
                                    # Create asymptotes
                                    if asymptote_value is None:  # This is for AI=(1/C#)+1
                                        ax.plot(x_values, x_values + 1, label="Carbon Clusters", color=color) 
                                        
                                    else:
                                        if  asymptote == "DBE = 0.5*C# (Aromatic)":
                                            ax.plot(x_values, [asymptote_value]*len(x_values)*x_values, label="Aromatic", color=color)
                                            
                                        elif  asymptote == "DBE = 0.67*C# (Condensed Aromatic)":
                                            ax.plot(x_values, [asymptote_value]*len(x_values)*x_values, label="Condensed Aromatic", color=color)
                                            
                                        elif  asymptote == "DBE = 0.735*C# - 0.5 (Cata-condensed PAHs)":
                                            ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) - 0.5, label="Cata-condensed PAHs", color=color)
                                            
                                        elif  asymptote == "DBE = 0.92*C# - 3.24 (Peri-condensed PAHs)":
                                            ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) - 3.24, label="Peri-condensed PAHs", color=color)
                                            
                                        elif  asymptote == "DBE = 0.9*C# (HC Cluster)":
                                            ax.plot(x_values, [asymptote_value]*len(x_values)*x_values, label="HC Cluster", color=color)
                                    
                            ax.legend()
                                
                        elif self.plot_option == "H# vs C#":
                            
                            # Set the axis limits based on the variables from the scale window
                            ax.set_xlim(self.C_num_min.get(), self.C_num_max.get())
                            ax.set_ylim(self.H_num_min.get(), self.H_num_max.get())
                            
                            # Define the asymptote details
                            asymptote_details = [
                                (6, 16, "H# = sqrt(6*C#) (Peri-condensed PAHs)"),
                                (0.5, 10, "H# = 0.5*C# + 3 (Cata-condensed PAHs)"),
                                (1, 2, "H# = C#"),
                                (1.25, 2, "H# = 1.25*C# + 2.5 (Aliphatic/Aromatic)"),
                                (2, 2, "H# = 2*C# + 2 (Aliphatic)")
                            ]
                                               
                            # Check if the asymptote is selected to be plotted
                            for asymptote_value, start_point, asymptote in asymptote_details:
                                if self.asymptote_vars.get(asymptote).get():
                                    x_values = np.linspace(start_point, ax.get_xlim()[1], 100)
                                    color = asymptote_colors[asymptote]
        
                                    # Create asymptotes
                                    if  asymptote == "H# = sqrt(6*C#) (Peri-condensed PAHs)":
                                        ax.plot(x_values, np.sqrt([asymptote_value]*len(x_values)*x_values), label="Peri-condensed PAHs", color=color)
                                        
                                    elif  asymptote == "H# = 0.5*C# + 3 (Cata-condensed PAHs)":
                                        ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) + 3, label="Cata-condensed PAHs", color=color)
                                        
                                    elif  asymptote == "H# = 1.25*C# + 2.5 (Aliphatic/Aromatic)":
                                        ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) + 2.5, label="Aliphatic/Aromatic", color=color)
                                        
                                    elif  asymptote == "H# = 2*C# + 2 (Aliphatic)":
                                        ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) + 2, label="Aliphatic", color=color)
                                        
                                    else:
                                        ax.plot(x_values, [asymptote_value]*len(x_values)*x_values, label="H# = C#", color=color)             
                                    
                            ax.legend()
                            
                        else:
                            # Set the axis limits based on the variables from the scale window
                            ax.set_xlim(self.Mass_min.get(), self.Mass_max.get())
                            ax.set_ylim(self.HC_min.get(), self.HC_max.get())
    
                        plt.colorbar(sc, ax=ax, label=intensity)
                        title = f'{sample} {description}, {group}'
                        self.show_plot(plot_func=None, fig=fig, title=title, x_data=group_data[x_col], y_data=group_data[y_col], z_data=group_data[intensity]) 

        else:
            grouped_data = self.displayed_data.groupby('Group')
            for group, group_data in grouped_data:
                
                # Check if the group are selected to be plotted
                if  self.group_vars.get(group, tk.BooleanVar(value=False)).get():
                    fig, ax = plt.subplots()
                    sc = ax.scatter(group_data[x_col], group_data[y_col], c=group_data[intensity], cmap='viridis', marker='.', norm=colors.LogNorm())
                    ax.set_xlabel(x_col)
                    ax.set_ylabel(y_col)
            
                    if self.plot_option == "DBE vs C#":
                        
                        # Set the axis limits based on the variables from the scale window
                        ax.set_xlim(self.C_num_min.get(), self.C_num_max.get())
                        ax.set_ylim(self.DBE_min.get(), self.DBE_max.get())
        
                        # Define the asymptote details
                        asymptote_details = [
                            (0.5, 6, "DBE = 0.5*C# (Aromatic)"),
                            (0.67, 10, "DBE = 0.67*C# (Condensed Aromatic)"),
                            (0.735, 10, "DBE = 0.735*C# - 0.5 (Cata-condensed PAHs)"),
                            (0.92, 16, "DBE = 0.92*C# - 3.24 (Peri-condensed PAHs)"),
                            (0.9, 6, "DBE = 0.9*C# (HC Cluster)"),
                            (None, 2, "DBE = C#+1 (Carbon Clusters)")
                        ]
                                                 
                        # Check if the asymptote is selected to be plotted
                        for asymptote_value, start_point, asymptote in asymptote_details:
                            if self.asymptote_vars.get(asymptote).get():
                                x_values = np.linspace(start_point, ax.get_xlim()[1], 100)
                                color = asymptote_colors[asymptote]
    
                                # Create asymptotes
                                if asymptote_value is None:  # This is for AI=(1/C#)+1
                                    ax.plot(x_values, x_values + 1, label="Carbon Clusters", color=color)
                                    
                                else:
                                    if  asymptote == "DBE = 0.5*C# (Aromatic)":
                                        ax.plot(x_values, [asymptote_value]*len(x_values)*x_values, label="Aromatic", color=color)
                                        
                                    elif  asymptote == "DBE = 0.67*C# (Condensed Aromatic)":
                                        ax.plot(x_values, [asymptote_value]*len(x_values)*x_values, label="Condensed Aromatic", color=color)
                                        
                                    elif  asymptote == "DBE = 0.735*C# - 0.5 (Cata-condensed PAHs)":
                                        ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) - 0.5, label="Cata-condensed PAHs", color=color)
                                        
                                    elif  asymptote == "DBE = 0.92*C# - 3.24 (Peri-condensed PAHs)":
                                        ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) - 3.24, label="Peri-condensed PAHs", color=color)
                                        
                                    elif  asymptote == "DBE = 0.9*C# (HC Cluster)":
                                        ax.plot(x_values, [asymptote_value]*len(x_values)*x_values, label="HC Cluster", color=color)
                                
                        ax.legend()
                            
                    elif self.plot_option == "H# vs C#":
                        
                        # Set the axis limits based on the variables from the scale window
                        ax.set_xlim(self.C_num_min.get(), self.C_num_max.get())
                        ax.set_ylim(self.H_num_min.get(), self.H_num_max.get())
                        
                        # Define the asymptote details
                        asymptote_details = [
                            (6, 16, "H# = sqrt(6*C#) (Peri-condensed PAHs)"),
                            (0.5, 10, "H# = 0.5*C# + 3 (Cata-condensed PAHs)"),
                            (1, 2, "H# = C#"),
                            (1.25, 2, "H# = 1.25*C# + 2.5 (Aliphatic/Aromatic)"),
                            (2, 2, "H# = 2*C# + 2 (Aliphatic)")
                        ]
                                           
                        # Check if the asymptote is selected to be plotted
                        for asymptote_value, start_point, asymptote in asymptote_details:
                            if self.asymptote_vars.get(asymptote).get():
                                x_values = np.linspace(start_point, ax.get_xlim()[1], 100)
                                color = asymptote_colors[asymptote]
    
                                # Create asymptotes
                                if  asymptote == "H# = sqrt(6*C#) (Peri-condensed PAHs)":
                                    ax.plot(x_values, np.sqrt([asymptote_value]*len(x_values)*x_values), label="Peri-condensed PAHs", color=color)
                                    
                                elif  asymptote == "H# = 0.5*C# + 3 (Cata-condensed PAHs)":
                                    ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) + 3, label="Cata-condensed PAHs", color=color)
                                    
                                elif  asymptote == "H# = 1.25*C# + 2.5 (Aliphatic/Aromatic)":
                                    ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) + 2.5, label="Aliphatic/Aromatic", color=color)
                                    
                                elif  asymptote == "H# = 2*C# + 2 (Aliphatic)":
                                    ax.plot(x_values, ([asymptote_value]*len(x_values)*x_values) + 2, label="Aliphatic", color=color)
                                    
                                else:
                                    ax.plot(x_values, [asymptote_value]*len(x_values)*x_values, label="H# = C#", color=color)             
                                
                        ax.legend()
                        
                    else:
                        # Set the axis limits based on the variables from the scale window
                        ax.set_xlim(self.Mass_min.get(), self.Mass_max.get())
                        ax.set_ylim(self.HC_min.get(), self.HC_max.get())
        
                    if intensity == 'Absolute intensity (Average)':
                        plt.colorbar(sc, ax=ax, label='Averaged absolute intensity')
                        
                    else:
                        plt.colorbar(sc, ax=ax, label='Averaged relative intensity')
                                        
                    # Constructing title parts from the unique_samples and unique_descriptions
                    title_parts = [f'{sample} {description}' for sample, description in zip(self.unique_samples, self.unique_descriptions)]
                    
                    # Constructing the final title
                    title = f"Average of {', '.join(title_parts[:-1])} & {title_parts[-1]}, {group}"
                        
                    self.show_plot(plot_func=None, fig=fig, title=title, x_data=group_data[x_col], y_data=group_data[y_col], z_data=group_data[intensity]) 

    def make_ai_plots(self, selected_groups):
        if self.displayed_data is None:
            messagebox.showerror("Error", "No data to plot. Please load data first.")
            return
        
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Relative intensity'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            intensity = 'Absolute intensity (Average)'
            
        else:
            intensity = 'Relative intensity (Average)'
            
        asymptote_colors = {
            "AI = 0.5 (Aromatic)": 'red',
            "AI = 0.67 (Condensed Aromatic)": 'blue',
            "AI = 0.735 - 0.5/C# (Cata-condensed PAHs)": 'green',
            "AI = 0.92 - 3.24/C# (Peri-condensed PAHs)": 'purple',
            "AI = 0.9 (HC Cluster)": 'orange',
            "AI = 1 + 1/C# (Carbon Clusters)": 'brown'
        }
        
        # Get the min and max intensity values from the user input
        intensity_min = self.intensity_min.get()
        intensity_max = self.intensity_max.get()
        
        # Create a custom logarithmic colormap normalization with the defined min and max values if they are set
        if intensity_min == 0.0 and intensity_max == 0.0:
            # default logarithmic scaling without custom min and max values
            custom_norm = colors.LogNorm()
              
        else:
            if intensity_min == 0.0 or intensity_max == 0.0:
                messagebox.showerror("Error", "The logarithm of 0 is not defined. Please enter another value")
            else:
                custom_norm = colors.LogNorm(vmin=intensity_min, vmax=intensity_max, clip=True)

        # Add new columns for DBE_AI and C#_AI
        self.displayed_data['DBE_AI'] = 1 + self.displayed_data['C#'] - self.displayed_data['O#'] - (self.displayed_data['H#'] / 2)
        self.displayed_data['C#_AI'] = self.displayed_data['C#'] - self.displayed_data['O#'] - self.displayed_data['N#']

        # Add AI column, set AI to 0 where DBE_AI or C#_AI are less than or equal to 0
        self.displayed_data['AI'] = self.displayed_data['DBE_AI'] / self.displayed_data['C#_AI']
        self.displayed_data.loc[(self.displayed_data['DBE_AI'] <= 0) | (self.displayed_data['C#_AI'] <= 0), 'AI'] = 0     

        self.create_group_column()
        
        if 'Sample' and 'Description' in self.displayed_data:
            for (sample, description), group_data in self.displayed_data.groupby(['Sample', 'Description']):
                
                # Check if the sample is selected to be plotted
                if self.sample_vars.get(f"{sample} - {description}", tk.BooleanVar(value=False)).get():
                    for selected_group in selected_groups:
                        
                        # Filter data for the selected group
                        group_data_selected = group_data[group_data['Group'] == selected_group]
    
                        # Create plot for selected group
                        fig, ax = plt.subplots()
                        sc = ax.scatter(group_data_selected['C#'], group_data_selected['AI'], c=group_data_selected[intensity], cmap='viridis', marker='.', norm=custom_norm)
                        ax.set_title(selected_group)
                        ax.set_xlabel('C#')
                        ax.set_ylabel('AI')
    
                        # Set the axis limits based on the variables from the scale window
                        ax.set_xlim(self.C_num_min.get(), self.C_num_max.get())
                        ax.set_ylim(self.AI_min.get(), self.AI_max.get())
    
                        # Define the asymptote details
                        asymptote_details = [
                            (0.5, 6, "AI = 0.5 (Aromatic)"),
                            (0.67, 10, "AI = 0.67 (Condensed Aromatic)"),
                            (0.735, 10, "AI = 0.735 - 0.5/C# (Cata-condensed PAHs)"),
                            (0.92, 16, "AI = 0.92 - 3.24/C# (Peri-condensed PAHs)"),
                            (0.9, 6, "AI = 0.9 (HC Cluster)"),
                            (None, 2, "AI = 1 + 1/C# (Carbon Clusters)")
                        ]
                        
                        # Check if the asymptote is selected to be plotted
                        for asymptote_value, start_point, asymptote in asymptote_details:
                            if self.asymptote_vars.get(asymptote).get():
                                x_values = np.linspace(start_point, ax.get_xlim()[1], 100)
                                color = asymptote_colors[asymptote]
    
                                # Create asymptotes
                                if asymptote_value is None:  # This is for AI=(1/C#)+1
                                    ax.plot(x_values, (1 / x_values) + 1, label="Carbon Clusters", color=color)
                                    
                                else:
                                    if  asymptote == "AI = 0.5 (Aromatic)":
                                        ax.plot(x_values, [asymptote_value]*len(x_values), label="Aromatic", color=color)
                                        
                                    elif  asymptote == "AI = 0.67 (Condensed Aromatic)":
                                        ax.plot(x_values, [asymptote_value]*len(x_values), label="Condensed Aromatic", color=color)
                                        
                                    elif  asymptote == "AI = 0.735 - 0.5/C# (Cata-condensed PAHs)":
                                        ax.plot(x_values, ([asymptote_value]*len(x_values)) - (0.5/x_values), label="Cata-condensed PAHs", color=color)
                                        
                                    elif  asymptote == "AI = 0.92 - 3.24/C# (Peri-condensed PAHs)":
                                        ax.plot(x_values, ([asymptote_value]*len(x_values)) - (3.24/x_values), label="Peri-condensed PAHs", color=color)
                                        
                                    elif  asymptote == "AI = 0.9 (HC Cluster)":
                                        ax.plot(x_values, [asymptote_value]*len(x_values), label="HC Cluster", color=color)
                                
                        ax.legend()
    
                        plt.colorbar(sc, ax=ax, label=intensity)
    
                        self.show_plot(plot_func=None, fig=fig, title=f"{sample} {description}, {selected_group}", x_data=group_data_selected['C#'], y_data=group_data_selected['AI'], z_data=group_data_selected[intensity])
                    
        else:
            grouped_data = self.displayed_data.groupby('Group')
            
            for group, group_data in grouped_data:
                
                # Check if the group are selected to be plotted
                if  self.group_vars.get(group, tk.BooleanVar(value=False)).get():
                    
                    # Create plot for selected group
                    fig, ax = plt.subplots()
                    sc = ax.scatter(group_data['C#'], group_data['AI'], c=group_data[intensity], cmap='viridis', marker='.', norm=colors.LogNorm())
                    ax.set_title(group)
                    ax.set_xlabel('C#')
                    ax.set_ylabel('AI')
    
                    # Set the axis limits based on the variables from the scale window
                    ax.set_xlim(self.C_num_min.get(), self.C_num_max.get())
                    ax.set_ylim(self.AI_min.get(), self.AI_max.get())
    
                    # Define the asymptote details
                    asymptote_details = [
                        (0.5, 6, "AI = 0.5 (Aromatic)"),
                        (0.67, 10, "AI = 0.67 (Condensed Aromatic)"),
                        (0.735, 10, "AI = 0.735 - 0.5/C# (Cata-condensed PAHs)"),
                        (0.92, 16, "AI = 0.92 - 3.24/C# (Peri-condensed PAHs)"),
                        (0.9, 6, "AI = 0.9 (HC Cluster)"),
                        (None, 2, "AI = 1 + 1/C# (Carbon Clusters)")
                    ]
                    
                    # Check if the asymptote is selected to be plotted
                    for asymptote_value, start_point, asymptote in asymptote_details:
                        if self.asymptote_vars.get(asymptote).get():
                            x_values = np.linspace(start_point, ax.get_xlim()[1], 100)
                            color = asymptote_colors[asymptote]
                            
                            # Create asymptotes
                            if asymptote_value is None:  # This is for AI=(1/C#)+1
                                ax.plot(x_values, (1 / x_values) + 1, label="Carbon Clusters", color=color)
                                
                            else:
                                if  asymptote == "AI = 0.5 (Aromatic)":
                                    ax.plot(x_values, [asymptote_value]*len(x_values), label="Aromatic", color=color)
                                    
                                elif  asymptote == "AI = 0.67 (Condensed Aromatic)":
                                    ax.plot(x_values, [asymptote_value]*len(x_values), label="Condensed Aromatic", color=color)
                                    
                                elif  asymptote == "AI = 0.735 - 0.5/C# (Cata-condensed PAHs)":
                                    ax.plot(x_values, ([asymptote_value]*len(x_values)) - (0.5/x_values), label="Cata-condensed PAHs", color=color)
                                    
                                elif  asymptote == "AI = 0.92 - 3.24/C# (Peri-condensed PAHs)":
                                    ax.plot(x_values, ([asymptote_value]*len(x_values)) - (3.24/x_values), label="Peri-condensed PAHs", color=color)
                                    
                                elif  asymptote == "AI = 0.9 (HC Cluster)":
                                    ax.plot(x_values, [asymptote_value]*len(x_values), label="HC Cluster", color=color)
                            
                    ax.legend()
                    
                    if intensity == 'Absolute intensity (Average)':
                        plt.colorbar(sc, ax=ax, label='Averaged absolute intensity')
                        
                    else:
                        plt.colorbar(sc, ax=ax, label='Averaged relative intensity')
                    
                    # Constructing title parts from the unique_samples and unique_descriptions
                    title_parts = [f'{sample} {description}' for sample, description in zip(self.unique_samples, self.unique_descriptions)]
                    
                    # Constructing the final title
                    title = f"Average of {', '.join(title_parts[:-1])} & {title_parts[-1]}, {group}"    
                    self.show_plot(plot_func=None, fig=fig, title=title, x_data=group_data['C#'], y_data=group_data['AI'], z_data=group_data[intensity])   
                
    def family_selection_window(self):
        
        def open_scale_selection_and_destroy():
            self.scale_selection_window(displayed_samples)
            family_selection_window.destroy()
        
        # Create new window
        family_selection_window = tk.Toplevel()
        family_selection_window.title("Select Families")
    
        # Center the window relative to the main window
        main_window = self.winfo_toplevel()
        main_window_x = main_window.winfo_x()
        main_window_y = main_window.winfo_y()
        main_window_width = main_window.winfo_width()
        main_window_height = main_window.winfo_height()
    
        comparison_window_x = main_window_x + (main_window_width // 2) - (300 // 2)
        comparison_window_y = main_window_y + (main_window_height // 2) - (200 // 2)
    
        family_selection_window.geometry(f"+{comparison_window_x}+{comparison_window_y}")
        
        if 'Sample' and 'Description' in self.displayed_data:
            # Extract selected samples
            selected_samples = [sample for sample, var in self.sample_vars.items() if var.get()]
        
            # Separate sample and description values
            sample_values = [sample.split(' - ')[0] for sample in selected_samples]
            description_values = [sample.split(' - ')[1] for sample in selected_samples]
        
            # Filter the displayed data to include only the selected samples
            displayed_samples = self.displayed_data[(self.displayed_data['Sample'].isin(sample_values)) &
                                                    (self.displayed_data['Description'].isin(description_values))]
            
        else:
            # Otherwise the selected samples does not need to be extracted
            displayed_samples = self.displayed_data
    
        # Get the unique families from the displayed samples
        families = displayed_samples['Family'].unique()
    
        # Create a dictionary to hold the family selection variables
        self.family_vars = {family: tk.BooleanVar() for family in families}
    
        for i, family in enumerate(families):
            # Create a checkbutton for each family
            ttk.Checkbutton(family_selection_window, text=family, variable=self.family_vars[family]).grid(row=i, column=0, sticky='w')
    
        # Add a "Next" button at the bottom of the window
        ttk.Button(family_selection_window, text="Next", command=open_scale_selection_and_destroy).grid(row=i+1, column=0)
        
    def scale_selection_window(self, displayed_samples):
        
        def plot_family_analysis_and_destroy():
            self.make_family_analysis_plot(displayed_samples)
            scale_selection_window.destroy()
        
        # Create new window
        scale_selection_window = tk.Toplevel()
        scale_selection_window.title("Select Y-scale")
    
        # Center the window relative to the main window
        main_window = self.winfo_toplevel()
        main_window_x = main_window.winfo_x()
        main_window_y = main_window.winfo_y()
        main_window_width = main_window.winfo_width()
        main_window_height = main_window.winfo_height()
    
        scale_window_x = main_window_x + (main_window_width // 2) - (300 // 2)
        scale_window_y = main_window_y + (main_window_height // 2) - (200 // 2)
    
        scale_selection_window.geometry(f"+{scale_window_x}+{scale_window_y}")
    
        # Initialize the scale variable
        self.scale_var = tk.StringVar()
    
        # Set the default scale
        self.scale_var.set("Linear Scale")
    
        scales = ["Linear Scale", "Logarithmic Scale"]
    
        for i, scale in enumerate(scales):
            # Create a radio button for each scale
            ttk.Radiobutton(scale_selection_window, text=scale, variable=self.scale_var, value=scale).grid(row=i, column=0, sticky='w')
    
        # Add a plot button at the bottom of the window
        ttk.Button(scale_selection_window, text="Plot", command=plot_family_analysis_and_destroy).grid(row=i+1, column=0)
    
    def make_family_analysis_plot(self, displayed_samples):
        
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Relative intensity'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            intensity = 'Absolute intensity (Average)'
            
        else:
            intensity = 'Relative intensity (Average)'
        
        predefined_order = [
            'Aliphatics', 'Aromatics', 'Condensed Aromatics', 'HC Clusters', 
            'Carbon Clusters', 'Fullerenes', 'Nitrogen Species', 
            'Oxygen Species', 'Nitrogen Oxygen Species', 'Elements', 
            'Organo-metallics'
            ]
    
        selected_families = [family for family, var in self.family_vars.items() if var.get()]
    
        # Arrange selected_families in predefined_order
        selected_families.sort(key=lambda x: predefined_order.index(x))
    
        n_families = len(selected_families)
    
        # Define the width of a bar
        bar_width = 0.8 / n_families
    
        # Create a color map for the families
        color_map = plt.get_cmap('tab10')
        family_colors = {family: color_map(i) for i, family in enumerate(selected_families)}
        
        if 'Sample' and 'Description' in self.displayed_data:
            sample_groups = displayed_samples.groupby(['Sample', 'Description'])
        
            for value_column, ylabel, plot_title in zip([intensity, 'Formula'], 
                                                        ['Sum of ' + intensity, 'Number of species'],
                                                        ['Family Analysis', 'Family Analysis']):
                
                # Track families that have been added to the legend
                added_to_legend = []
                
                # Generate the bar plot for each sample
                fig, ax = plt.subplots()
        
                # Initialize the x position for the first bar
                x_pos = 0
        
                # Create a list to store the x positions of the middle of each bar group
                group_centers = []
        
                for (sample, description), group_data in sample_groups:
                    # Filter the data to include only the selected families
                    filtered_data = group_data[group_data['Family'].isin(selected_families)]
        
                    if value_column == intensity:
                        # Group the data by 'Family' and calculate the sum of the absolute intensity for each group
                        bar_data = filtered_data.groupby('Family')[value_column].sum().reindex(selected_families, fill_value=0)
                    else:  # 'Formula'
                        # Group the data by 'Family' and calculate the unique count for each group
                        bar_data = filtered_data.groupby('Family')[value_column].nunique().reindex(selected_families, fill_value=0)
        
                    # Record the start x position of this group
                    group_start_x = x_pos
        
                    for i, (family, value) in enumerate(bar_data.items()):
                        if value > 0:  # Only plot the bar if the value is greater than 0
                            label = family if family not in added_to_legend else ""
                            ax.bar(x_pos, value, width=bar_width, color=family_colors[family], label=label)
                            x_pos += bar_width
                
                            # If the family was added to the legend, mark it as added
                            if family not in added_to_legend:
                                added_to_legend.append(family)
        
                    # Store the x position of the middle of the group
                    group_centers.append(group_start_x + (x_pos - group_start_x - bar_width) / 2)
        
                    # Define the space between bar groups based on the number of bars
                    space_between_groups = 0.4 + (x_pos - group_start_x)
        
                    # Update the x position for the next bar group
                    x_pos = group_start_x + space_between_groups
        
                # Set the y-axis scale based on the selected option
                y_scale = self.scale_var.get()
                ax.set_yscale('log' if y_scale == "Logarithmic Scale" else 'linear')
        
                # Set the x-axis ticks to be the sample names
                sample_names = [f"{sample}, {description}" for sample, description in sample_groups.groups.keys()]
                ax.set_xticks(group_centers)
                ax.set_xticklabels(sample_names, rotation=0)
        
                ax.set_xlabel('Sample')
                ax.set_ylabel(ylabel)
                ax.set_title('Family Analysis')
                ax.legend(title='Family')
        
                self.show_plot(plot_func=None, fig=fig, title=plot_title)

        else:       
            # Filter the data to include only the selected families
            filtered_data = self.displayed_data[self.displayed_data['Family'].isin(selected_families)]
            
            # Define the bar width. You can adjust this as needed.
            bar_width = 1
            
            # Create an array for the x positions of the bars
            x_pos = np.arange(len(selected_families))
            
            # Create a dictionary mapping families to colors using the color map
            color_map = plt.get_cmap('tab10')
            family_colors = {family: color_map(i) for i, family in enumerate(selected_families)}
            
            # Constructing title parts from the unique_samples and unique_descriptions
            title_parts = [f'{sample} {description}' for sample, description in zip(self.unique_samples, self.unique_descriptions)]
            
            # Constructing the final title
            sample_name = f"Average of {', '.join(title_parts[:-1])} & {title_parts[-1]}"
            
            # Metrics to be plotted
            metrics = [
                {
                    'value': filtered_data.groupby(['Family'])[intensity].sum().reindex(selected_families, fill_value=0),
                    'ylabel': 'Sum of average absolute intensity' if intensity == 'Absolute intensity (Average)' else 'Sum of average relative intensity',
                    'title': 'Family Analysis'
                },
                {
                    'value': filtered_data.groupby('Family')['Formula'].nunique().reindex(selected_families, fill_value=0),
                    'ylabel': 'Number of species',
                    'title': 'Family Analysis'
                }
            ]
            
            # Loop through metrics to create the plots
            for metric in metrics:
                fig, ax = plt.subplots()
                for i, (family, value) in enumerate(metric['value'].items()):
                    ax.bar(x_pos[i], value, width=bar_width, color=family_colors[family], label=family)
            
                y_scale = self.scale_var.get()
                ax.set_yscale('log' if y_scale == "Logarithmic Scale" and metric['title'] == 'Family Analysis' else 'linear')
                ax.set_xticks([])
                ax.set_ylabel(metric['ylabel'])
                ax.set_title(metric['title'])
                ax.legend(title='Family')
            
                plt.text(0.5, -0.05, sample_name, ha='center', va='center', transform=ax.transAxes)
            
                self.show_plot(plot_func=None, fig=fig, title=metric['title'])
            
    def plot_common_species(self, selected_groups):
        
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Relative intensity'
            
        # Get the min and max intensity values from the user input
        intensity_min = self.intensity_min.get()
        intensity_max = self.intensity_max.get()
        
        # Create a custom logarithmic colormap normalization with the defined min and max values if they are set
        if intensity_min == 0.0 and intensity_max == 0.0:
            # default logarithmic scaling without custom min and max values
            custom_norm = colors.LogNorm()
              
        else:
            if intensity_min == 0.0 or intensity_max == 0.0:
                messagebox.showerror("Error", "The logarithm of 0 is not defined. Please enter another value")
            else:
                custom_norm = colors.LogNorm(vmin=intensity_min, vmax=intensity_max, clip=True)
        
        # Create group column
        self.create_group_column()
        
        filtered_data = {group: pd.DataFrame() for group in selected_groups}
        
        # Filter data based os selected groups
        for (sample, description), group_data in self.displayed_data.groupby(['Sample', 'Description']):
            if self.sample_vars.get(f"{sample} - {description}", tk.BooleanVar(value=False)).get():
                for selected_group in selected_groups:
                    group_data_filtered = group_data[group_data['Group'] == selected_group]                   
                    filtered_data[selected_group] = pd.concat([filtered_data[selected_group], group_data_filtered])
        
        # Generated the plot for each selected group
        for selected_group in selected_groups:
            sample_counts = filtered_data[selected_group].groupby(['Sample', 'Description'])['Formula'].count()
        
            most_data_sample = sample_counts.idxmax()
            least_data_sample = sample_counts.idxmin() if len(sample_counts) > 1 else most_data_sample
        
            most_data = filtered_data[selected_group][(filtered_data[selected_group]['Sample'] == most_data_sample[0]) & 
                                                      (filtered_data[selected_group]['Description'] == most_data_sample[1])]
            least_data = filtered_data[selected_group][(filtered_data[selected_group]['Sample'] == least_data_sample[0]) & 
                                                       (filtered_data[selected_group]['Description'] == least_data_sample[1])]
    
            common_data = pd.merge(most_data, least_data, how='inner', on='Formula', suffixes=('_most', '_least'))
            
            common_data = common_data.drop(columns=[col for col in common_data.columns if col.endswith('_least')])
            
            common_data.columns = [col.replace('_most', '') for col in common_data.columns]
            
            # Count the number of unique species in the 'Least' and 'Common' data samples
            num_least_species = least_data['Formula'].nunique()
            num_common_species = common_data['Formula'].nunique()
    
            # Calculate the percentage of common species
            perc_common_species = (num_common_species / num_least_species) * 100
    
            # Define the same scale for x and y axes
            x_limit = [self.C_num_min.get(), self.C_num_max.get()]
            y_limit = [self.DBE_min.get(), self.DBE_max.get()]
    
            # Create subplots
            fig, axs = plt.subplots(1, 3, figsize=(20, 20))
        
            # Scatter plots
            scatter = axs[0].scatter(most_data['C#'], most_data['DBE'], c=most_data[intensity], cmap='viridis', marker='.', norm=custom_norm)
            axs[0].set_title(f'{most_data_sample[0]} {most_data_sample[1]}')
            axs[0].set_xlabel('C#')
            axs[0].set_ylabel('DBE')
            axs[0].set_xlim(x_limit[0], x_limit[1])
            axs[0].set_ylim(y_limit[0], y_limit[1])
            axs[0].set_aspect('equal', adjustable='box')
    
            axs[1].scatter(least_data['C#'], least_data['DBE'], c=least_data[intensity], cmap='viridis', marker='.', norm=custom_norm)
            axs[1].set_title(f'{least_data_sample[0]} {least_data_sample[1]}')
            axs[1].set_xlabel('C#')
            axs[1].set_ylabel('DBE')
            axs[1].set_xlim(x_limit[0], x_limit[1])
            axs[1].set_ylim(y_limit[0], y_limit[1])
            axs[1].set_aspect('equal', adjustable='box')
    
            axs[2].scatter(common_data['C#'], common_data['DBE'], c=common_data[intensity], cmap='viridis', marker='.', norm=custom_norm)
            axs[2].set_title(f'Common data ({perc_common_species:.2f}%)')
            axs[2].set_xlabel('C#')
            axs[2].set_ylabel('DBE')
            axs[2].set_xlim(x_limit[0], x_limit[1])
            axs[2].set_ylim(y_limit[0], y_limit[1])
            axs[2].set_aspect('equal', adjustable='box')
    
            # Add a colorbar
            fig.subplots_adjust(right=0.8)
            cbar_ax = fig.add_axes([0.85, 0.333, 0.05, 0.325])
            fig.colorbar(scatter, cax=cbar_ax, label=intensity)
        
            self.show_plot(plot_func=None, fig=fig)

    def show_plot(self, plot_func, data=None, title='', fig=None, x_data=None, y_data=None, z_data=None):
        
        # Store the x and y data for saving it later
        self.x_data = x_data
        self.y_data = y_data
        self.z_data = z_data

        if fig is None:
            fig, ax = plt.subplots()
            plot_func(ax, data)
            
        else:
            ax = fig.gca()
            
        # Add minor ticks
        if self.plot_option == 'Family Analysis':
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
            
        else:
            ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

        ax.set_title(title)

        plot_window = tk.Toplevel(self.master)
        plot_window.title(title)
        
        # Set the size of the new window
        plot_window.geometry("800x600")
        
        # Center the comparison window relative to the main window
        main_window = self.winfo_toplevel()
        main_window_x = main_window.winfo_x()
        main_window_y = main_window.winfo_y()
        main_window_width = main_window.winfo_width()
        main_window_height = main_window.winfo_height()
    
        comparison_window_x = main_window_x + (main_window_width // 2) - (800 // 2)
        comparison_window_y = main_window_y + (main_window_height // 2) - (600 // 2)
    
        plot_window.geometry(f"+{comparison_window_x}+{comparison_window_y}")

        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add a "Save" button at the bottom of the plot
        save_button = tk.Button(plot_window, text="Save", command=lambda: self.save_plot(fig))
        save_button.pack(side=tk.BOTTOM, padx=5, pady=5)
            
    def save_plot(self, fig):
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Relative intensity'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            intensity = 'Absolute intensity (Average)'
            
        else:
            intensity = 'Relative intensity (Average)'
        
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("SVG files", "*.svg"), ("PDF files", "*.pdf"), ("EPS files", "*.eps")])
    
        if file_path:
            fig.savefig(file_path)
            messagebox.showinfo("Info", "Plot saved successfully.")
            
            if self.x_data is not None and self.y_data is not None and self.z_data is not None:
                
                # Get the directory from the plot file path
                initial_dir = os.path.dirname(file_path)
                
                # Ask the user to select the file format for the data file, opening the dialog in the same directory
                data_file_path = filedialog.asksaveasfilename(initialdir=initial_dir, defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
    
                if data_file_path:
                    y_label, x_label = self.plot_option.split(' vs ')
                    data = pd.DataFrame({
                        x_label: self.x_data,
                        y_label: self.y_data,
                        intensity: self.z_data
                    })
                    data.to_csv(data_file_path, sep=',', index=False)
                    messagebox.showinfo("Info", "Data saved successfully.")
                    
                else:
                    messagebox.showerror("Error", "No file selected. Please select a file to save the data.")
    
        else:
            messagebox.showerror("Error", "No file selected. Please select a file to save the plot.")
            
            

    def export_data(self, data):
        if self.displayed_data is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                      filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")])
    
            if file_path:
                # Export as CSV for both CSV and TXT extensions
                self.displayed_data.to_csv(file_path, index=False, sep=',')
    
                messagebox.showinfo("Info", "Data exported successfully.")
                
            else:
                messagebox.showerror("Error", "No file selected. Please select a file to export.")
                
        else:
            messagebox.showerror("Error", "No data to export. Please load data first.")
            
class FamiliesDialog(simpledialog.Dialog):
    
    def __init__(self, parent, all_families, selected_families):
        self.all_families = all_families
        self.selected_families = selected_families
        super().__init__(parent, title="Select Families")

    # Create dialog window with all a list of all families
    def body(self, parent):
        self.vars = {family: tk.BooleanVar(value=family in self.selected_families) for family in self.all_families}
        
        # Add checkbutton next each family
        for i, family in enumerate(self.all_families):
            ttk.Checkbutton(parent, text=family, variable=self.vars[family]).grid(row=i, column=0, sticky='w')

    def apply(self):
        
        # Store the selected families
        self.result = [family for family, var in self.vars.items() if var.get()]

class FilterDialog(simpledialog.Dialog):
    
    def __init__(self, parent, displayed_data, filter_callback):
        self.displayed_data = displayed_data
        self.filter_callback = filter_callback
        self.vars = []
        super().__init__(parent, title="Filter Data")

    def body(self, parent):
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Abs. Intensity'
            mass = 'Mass'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Rel. Intensity'
            mass = 'Mass'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            intensity = 'Abs. Intensity (Avg)'
            mass = 'Mass (Avg)'
            
        else:
            intensity = 'Rel. Intensity (Avg)'
            mass = 'Mass (Avg)'
        
        labels = ["Family:", "C# Min:", "C# Max:", "C# Ranges:", mass + " Min:", mass + " Max:", "Mass Ranges:", intensity + " Min:", intensity + " Max:"]
        
        self.vars = [tk.StringVar() for _ in range(len(labels))]
        entries = []

        # Handling Family line
        ttk.Label(parent, text=labels[0]).grid(row=0, column=0, padx=5, pady=5)
        self.family_button = ttk.Button(parent, text="Select Families", command=self.select_families)
        self.family_button.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Update", command=self.update_ranges).grid(row=0, column=2, padx=5, pady=5)

        # Handling C#, Mass and Abs. Intensity lines
        for i in range(3):  # i will be 0 for C#, 1 for Mass, 2 for Abs. Intensity
            # Min Label and Entry
            ttk.Label(parent, text=labels[i*3+1]).grid(row=i+1, column=0, padx=5, pady=5)
            entry_min = ttk.Entry(parent, textvariable=self.vars[i*3+1])
            entry_min.grid(row=i+1, column=1, padx=5, pady=5)
            entries.append(entry_min)
            
            # Max Label and Entry
            ttk.Label(parent, text=labels[i*3+2]).grid(row=i+1, column=2, padx=5, pady=5)
            entry_max = ttk.Entry(parent, textvariable=self.vars[i*3+2])
            entry_max.grid(row=i+1, column=3, padx=5, pady=5)
            entries.append(entry_max)

            # All Button
            ttk.Button(parent, text="All", command=self.create_update_command(i)).grid(row=i+1, column=4, padx=5, pady=5)

            # Ranges Label and Entry (only for C# and Mass)
            if i < 2:
                ttk.Label(parent, text=labels[i*3+3]).grid(row=i+1, column=5, padx=5, pady=5)
                entry_range = ttk.Entry(parent, textvariable=self.vars[i*3+3])
                entry_range.grid(row=i+1, column=6, padx=5, pady=5)
                entries.append(entry_range)
                entry_range.bind("<FocusIn>", self.clear_min_max(i))
                entry_min.bind("<FocusIn>", self.clear_ranges(i))
                entry_max.bind("<FocusIn>", self.clear_ranges(i))

        return entries[0]

    # Clear max/min entry fields when pressing the ranges entry field
    def clear_min_max(self, index):
        
        def inner_clear(event):
            self.vars[index*3+1].set("")
            self.vars[index*3+2].set("")
        return inner_clear

    # Clear ranges entry field when pressing the max/min entry fields
    def clear_ranges(self, index):
        
        def inner_clear(event):
            self.vars[index*3+3].set("")
        return inner_clear
    
    # Update entry fields based on selected families
    def create_update_command(self, index):
        commands = [self.update_c, self.update_mass, self.update_abs_intensity]
        return commands[index]

    # Apply filters
    def apply(self):
        family_filter = self.vars[0].get()
        
        c_min_max = (float(self.vars[1].get()), float(self.vars[2].get())) if self.vars[1].get() and self.vars[2].get() else None
        c_ranges = self.parse_ranges(self.vars[3].get()) if self.vars[3].get() else None
    
        mass_min_max = (float(self.vars[4].get()), float(self.vars[5].get())) if self.vars[4].get() and self.vars[5].get() else None
        mass_ranges = self.parse_ranges(self.vars[6].get()) if self.vars[6].get() else None
    
        intensity_min_max = (float(self.vars[7].get()), float(self.vars[8].get())) if self.vars[7].get() and self.vars[8].get() else None
    
        if family_filter:
            self.filter_callback(family_filter, c_min_max, mass_min_max, intensity_min_max, c_ranges, mass_ranges)
            
        else:
            messagebox.showwarning("Warning", "Please enter a valid Family filter.")
    
    def parse_ranges(self, ranges):
        # Method to parse the range strings into a list of tuples
        if not ranges:
            return None
        
        ranges = ranges.split(',')
        return [tuple(map(float, r.split('-'))) for r in ranges]

    # Select families
    def select_families(self):
        all_families = set(self.displayed_data['Family'])
        selected_families = self.vars[0].get().split(',')
        dialog = FamiliesDialog(self, all_families, selected_families)
        selected_families = dialog.result
        
        if selected_families is not None:
            self.vars[0].set(','.join(selected_families))

    def set_all_families(self):
        all_families = set(self.displayed_data['Family'])
        self.vars[0].set(','.join(all_families))

    # Update entry fields based on selected families
    def update_ranges(self):
        selected_families = self.vars[0].get().split(',')
        selected_data = self.displayed_data[self.displayed_data['Family'].isin(selected_families)]
            
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            mass = 'Mass'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Relative intensity'
            mass = 'Mass'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            intensity = 'Absolute intensity (Average)'
            mass = 'Mass (Average)'
            
        else:
            intensity = 'Relative intensity (Average)'
            mass = 'Mass (Average)'
        
        for i, column in enumerate(['C#', mass, intensity]):
            
            if not selected_data[column].empty:
                min_val = min(selected_data[column])
                max_val = max(selected_data[column])
                self.vars[i*3+1].set(min_val)
                self.vars[i*3+2].set(max_val)
                
            else:
                self.vars[i*3+1].set("")
                self.vars[i*3+2].set("")

    def update_c(self):
        selected_families = self.vars[0].get().split(',')
        selected_data = self.displayed_data[self.displayed_data['Family'].isin(selected_families)]
        
        self.vars[1].set(min(selected_data['C#']))
        self.vars[2].set(max(selected_data['C#']))

    def update_mass(self):
        
        if 'Absolute intensity' in self.displayed_data:
            mass = 'Mass'
            
        elif 'Relative intensity' in self.displayed_data:
            mass = 'Mass'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            mass = 'Mass (Average)'
            
        else:
            mass = 'Mass (Average)'
            
        selected_families = self.vars[0].get().split(',')
        selected_data = self.displayed_data[self.displayed_data['Family'].isin(selected_families)]
        
        self.vars[4].set(min(selected_data[mass]))
        self.vars[5].set(max(selected_data[mass]))

    def update_abs_intensity(self):
        
        if 'Absolute intensity' in self.displayed_data:
            intensity = 'Absolute intensity'
            
        elif 'Relative intensity' in self.displayed_data:
            intensity = 'Relative intensity'
            
        elif 'Absolute intensity (Average)' in self.displayed_data:
            intensity = 'Absolute intensity (Average)'
            
        else:
            intensity = 'Relative intensity (Average)'
            
        selected_families = self.vars[0].get().split(',')
        selected_data = self.displayed_data[self.displayed_data['Family'].isin(selected_families)]
        
        self.vars[7].set(min(selected_data[intensity]))
        self.vars[8].set(max(selected_data[intensity]))

    def buttonbox(self):
        # Override the default buttonbox method to create ttk buttons
        box = ttk.Frame(self)
    
        ok_button = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        ok_button.pack(side=tk.LEFT, padx=5, pady=5)
        cancel_button = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        cancel_button.pack(side=tk.LEFT, padx=5, pady=5)
    
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

if __name__ == "__main__":
    
    app = DataFilterApp()
    app.mainloop()