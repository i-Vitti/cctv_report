import os
import sys
import subprocess
import importlib

# Get the current Python version
python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

# Update paths dynamically based on Python version
os.environ["PATH"] += os.pathsep + f"/home/appuser/.local/bin"
sys.path.extend([
    f"/home/appuser/.local/lib/python{python_version}/site-packages",
    f"/home/adminuser/venv/lib/python{python_version}/site-packages",
])

# Ensure pdfplumber is installed
try:
    import pdfplumber
except ModuleNotFoundError:
    print("pdfplumber not found. Attempting installation...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "pdfplumber"], check=True)
        importlib.invalidate_caches()
        sys.path.append(f"/home/adminuser/venv/lib/python{python_version}/site-packages")
        pdfplumber = importlib.import_module("pdfplumber")
        print("pdfplumber installed successfully.")
    except Exception as e:
        print(f"Failed to install pdfplumber: {e}. Please install it manually.")
        sys.exit(1)

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
            extracted_values.append(f"{table1.iloc[2, 5]}")
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
    st.title("CCTV Data Extractor App")
    uploaded_files = st.file_uploader("Upload PDF CCTV reports", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            extracted_values = extract_pdf_content(uploaded_file)
            
            # Display extracted values
            st.subheader(f"Extracted Data from {uploaded_file.name}")
            for value in extracted_values:
                st.write(value)

if __name__ == "__main__":
    main()
