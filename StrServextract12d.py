import os
import subprocess
import sys

# Ensure system paths are recognized
os.environ["PATH"] += os.pathsep + "/home/appuser/.local/bin"
sys.path.append("/home/appuser/.local/lib/python3.9/site-packages")

# Force install pdfplumber if missing
try:
    import pdfplumber
except ModuleNotFoundError:
    print("pdfplumber not found. Installing...")
    subprocess.run(["pip", "install", "--no-cache-dir", "pdfplumber", "pdfminer.six"])
    import importlib
    importlib.invalidate_caches()
    import pdfplumber  # Import again after installation

import pandas as pd
import streamlit as st

# Function to extract specific table data from a PDF file
def extract_pdf_content(pdf_path):
    extracted_data = {'text': [], 'tables': []}
    extracted_values = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text
            extracted_data['text'].append(page.extract_text())
            
            # Extract tables
            tables = page.extract_tables()
            if tables:
                for table in tables[:2]:  # Only extracting the first two tables
                    df = pd.DataFrame(table)
                    extracted_data['tables'].append(df)
    
    # Extract specific required values
    if len(extracted_data['tables']) >= 2:
        table1, table2 = extracted_data['tables'][0], extracted_data['tables'][1]
        
        # Extracting required values safely
        try:
            extracted_values.append(f"{table1.iloc[2, 0]}")
        except IndexError:
            extracted_values.append("Not found")
        
        try:
            extracted_values.append(f"{table1.iloc[3, 0]}")
        except IndexError:
            extracted_values.append("Not found")
        
        try:
            extracted_values.append(f"{table2.iloc[4, 5]}")
        except IndexError:
            extracted_values.append("Not found")
        
        try:
            extracted_values.append(f"{table2.iloc[5, 5]}")
        except IndexError:
            extracted_values.append("Not found")
        
        try:
            extracted_values.append(f"{table2.iloc[4, 11]}")
        except IndexError:
            extracted_values.append("Not found")
        
        try:
            extracted_values.append(f"{table2.iloc[5, 11]}")
        except IndexError:
            extracted_values.append("Not found")
    
    return extracted_values

# Streamlit App
def main():
    st.title("PDF Data Extractor App")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        extracted_values = extract_pdf_content(uploaded_file)
        
        # Display extracted values
        st.subheader("Extracted Specific Table Values")
        for value in extracted_values:
            st.write(value)

if __name__ == "__main__":
    main()
