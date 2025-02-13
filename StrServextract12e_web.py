import os
import sys
import subprocess
import importlib
import pandas as pd
import streamlit as st

# Get the current Python version
python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

# Update paths dynamically based on Python version
os.environ["PATH"] += os.pathsep + f"/home/appuser/.local/bin"
sys.path.extend([
    f"/home/appuser/.local/lib/python{python_version}/site-packages",
    f"/home/adminuser/venv/lib/python{python_version}/site-packages",
])

# Ensure pdfplumber is installed and recognized
try:
    import pdfplumber
except ModuleNotFoundError:
    print("pdfplumber not found. Attempting installation...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pdfplumber", "--target", os.path.expanduser(f"~/.local/lib/python{python_version}/site-packages")], check=True)
        importlib.invalidate_caches()
        sys.path.append(os.path.expanduser(f"~/.local/lib/python{python_version}/site-packages"))
        import pdfplumber
        print("pdfplumber installed successfully.")
    except Exception as e:
        print(f"Failed to install pdfplumber: {e}. Please install it manually.")
        sys.exit(1)

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
        extracted_rows = []
        try:
            extracted_rows.append([table1.iloc[2, 0], table1.iloc[2, 5]])
        except IndexError:
            extracted_rows.append(["Not found", "Not found"])
        
        try:
            extracted_rows.append([table2.iloc[4, 5], table2.iloc[4, 11]])
        except IndexError:
            extracted_rows.append(["Not found", "Not found"])
        
        try:
            extracted_rows.append([table2.iloc[5, 5], table2.iloc[5, 11]])
        except IndexError:
            extracted_rows.append(["Not found", "Not found"])
        
        extracted_values = pd.DataFrame(extracted_rows, columns=["Column1", "Column2"])
    
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
            st.dataframe(extracted_values)
            
            # Provide download option
            csv = extracted_values.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name=f"extracted_data_{uploaded_file.name}.csv",
                mime='text/csv',
            )

if __name__ == "__main__":
    main()
