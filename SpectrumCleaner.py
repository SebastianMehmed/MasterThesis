#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 03:15:13 2023

@author: aroma
"""

import xml.etree.ElementTree as ET
import os

# Define your file path
file_path = "Wisconsin_Bulk.msd"

# Extract the base filename without the extension
base_filename = os.path.splitext(os.path.basename(file_path))[0]

# Append '_cleaned' to the filename and add back the extension
new_filename = base_filename + '_cleaned.msd'

# Open the file as a text file
with open(file_path, 'r') as file:
    file_content = file.read()

# Parse the XML content from the file
root = ET.fromstring(file_content)

# Find the annotations in the XML tree
annotations_xml = root.find('.//annotations')

# Create a list to hold the annotations
annotations_list = []

# Iterate over the annotation elements in the XML
for annotation in annotations_xml:
    # Get the attributes of the annotation
    peak_mz = float(annotation.attrib['peakMZ'])
    calc_mz = float(annotation.attrib['calcMZ'])
    formula = annotation.attrib['formula']
    
    # Calculate the error as the absolute difference between peakMZ and calcMZ
    error = abs(peak_mz - calc_mz)
    
    # Calculate the molecular complexity as the number of distinct atoms in the formula
    # We assume that each capital letter represents a new type of atom
    molecular_complexity = len([char for char in formula if char.isupper()])
    
    # Add the annotation to the list
    annotations_list.append((peak_mz, formula, molecular_complexity, error, annotation))

# Sort the annotations by peakMZ, then by molecular complexity, then by error
annotations_list.sort(key=lambda x: (x[0], x[2], x[3]))

annotations_list[:5]  # Show the first 5 annotations for verification

# Create a new list to hold the non-duplicate annotations
non_duplicate_annotations = []

# Initialize variables to track the current peakMZ and formula
current_peak_mz = None
current_formula = None

# Iterate over the sorted annotations
for peak_mz, formula, molecular_complexity, error, annotation in annotations_list:
    # If the peakMZ has changed, we add the annotation to the non-duplicate list
    # This works because we sorted the annotations by peakMZ, molecular complexity, and error
    # So, the first annotation we see for each peakMZ will have the lowest molecular complexity
    if peak_mz != current_peak_mz:
        non_duplicate_annotations.append((peak_mz, formula, molecular_complexity, error, annotation))
        current_peak_mz = peak_mz

# Now we have removed duplicates based on peakMZ. Next, we remove duplicates based on formula
# We sort the non-duplicate annotations by formula, then by error
non_duplicate_annotations.sort(key=lambda x: (x[1], x[3]))

# Create a final list to hold the annotations with no duplicates in peakMZ or formula
final_annotations = []

# Iterate over the sorted non-duplicate annotations
for peak_mz, formula, molecular_complexity, error, annotation in non_duplicate_annotations:
    # If the formula has changed, we add the annotation to the final list
    # This works because we sorted the annotations by formula, then by error
    # So, the first annotation we see for each formula will have the lowest error
    if formula != current_formula:
        final_annotations.append((peak_mz, formula, molecular_complexity, error, annotation))
        current_formula = formula

final_annotations[:5]  # Show the first 5 final annotations for verification

# Create a new annotations element
new_annotations_xml = ET.Element('annotations')

# Sort the final annotations by peakMZ
final_annotations.sort(key=lambda x: x[0])

# Add the final annotations to the new annotations element
for peak_mz, formula, molecular_complexity, error, annotation in final_annotations:
    new_annotations_xml.append(annotation)

# Replace the old annotations element with the new one in the root of the XML tree
for i, child in enumerate(root):
    if child.tag == 'annotations':
        root[i] = new_annotations_xml
        break

# Convert the updated XML tree back into a string
new_file_content = ET.tostring(root, encoding='unicode')

# Write the new file content to a new file
with open(file_path, 'w') as file:
    file.write(new_file_content)