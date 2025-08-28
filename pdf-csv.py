import pdfplumber
import pandas as pd
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def is_date(text):
    """Check if the text matches a date format (e.g., DD/MM/YYYY)."""
    if not text or text == '-':
        return False
    return bool(re.match(r'\d{2}/\d{2}/\d{4}', text))

def is_amount(text):
    """Check if the text is a monetary amount (e.g., 123.45 or 0.0)."""
    if not text or text == '-':
        return False
    return bool(re.match(r'^-?\d{1,3}(,\d{3})*(\.\d{2})?$', text.replace(',', '')))

def extract_transactions(pdf_path):
    """Extract transactions from the ICICI bank statement PDF."""
    transactions = []
    headers = ['S No.', 'Value Date', 'Transaction Date', 'Cheque Number', 'Transaction Remarks', 
               'Withdrawal Amount (INR)', 'Deposit Amount (INR)', 'Balance (INR)']
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                logging.info(f"Processing page {page_num}")
                
                # Try to extract tables
                tables = page.extract_tables()
                if tables:
                    logging.info(f"Found {len(tables)} table(s) on page {page_num}")
                    for table in tables:
                        # Skip header row if it matches expected headers
                        if any(h in table[0] for h in headers):
                            table = table[1:]  # Skip header row
                        for row in table:
                            # Ensure row has enough columns and no None values
                            if len(row) >= 8 and all(cell is not None for cell in row):
                                try:
                                    transaction = {
                                        'S No.': row[0].strip(),
                                        'Value Date': row[1].strip(),
                                        'Transaction Date': row[2].strip(),
                                        'Cheque Number': row[3].strip(),
                                        'Transaction Remarks': ' '.join(row[4].split()),  # Clean multi-line remarks
                                        'Withdrawal Amount (INR)': row[5].strip(),
                                        'Deposit Amount (INR)': row[6].strip(),
                                        'Balance (INR)': row[7].strip()
                                    }
                                    # Validate key fields
                                    if is_date(transaction['Transaction Date']) and is_amount(transaction['Balance (INR)']):
                                        transactions.append(transaction)
                                    else:
                                        logging.warning(f"Skipping invalid row on page {page_num}: {row}")
                                except AttributeError as e:
                                    logging.error(f"Error processing row on page {page_num}: {row}, Error: {e}")
                            else:
                                logging.warning(f"Skipping incomplete or None-containing row on page {page_num}: {row}")
                
                # Fallback to text parsing if no tables are found
                else:
                    logging.info(f"No tables found on page {page_num}, falling back to text parsing")
                    text = page.extract_text()
                    if not text:
                        logging.warning(f"No text extracted from page {page_num}")
                        continue
                    lines = text.split('\n')
                    current_transaction = None
                    transaction_data = []
                    
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Check if line starts with a serial number (indicating new transaction)
                        if re.match(r'^\d+\s*$', line):
                            if current_transaction:
                                # Save previous transaction if valid
                                if len(transaction_data) >= 8:
                                    try:
                                        transaction = {
                                            'S No.': transaction_data[0],
                                            'Value Date': transaction_data[1],
                                            'Transaction Date': transaction_data[2],
                                            'Cheque Number': transaction_data[3],
                                            'Transaction Remarks': ' '.join(transaction_data[4:-3]),
                                            'Withdrawal Amount (INR)': transaction_data[-3],
                                            'Deposit Amount (INR)': transaction_data[-2],
                                            'Balance (INR)': transaction_data[-1]
                                        }
                                        if is_date(transaction['Transaction Date']) and is_amount(transaction['Balance (INR)']):
                                            transactions.append(transaction)
                                        else:
                                            logging.warning(f"Skipping invalid text transaction on page {page_num}: {transaction_data}")
                                    except Exception as e:
                                        logging.error(f"Error processing text transaction on page {page_num}: {transaction_data}, Error: {e}")
                            transaction_data = [line]
                            current_transaction = True
                        elif current_transaction:
                            transaction_data.append(line)
                    
                    # Save the last transaction
                    if current_transaction and len(transaction_data) >= 8:
                        try:
                            transaction = {
                                'S No.': transaction_data[0],
                                'Value Date': transaction_data[1],
                                'Transaction Date': transaction_data[2],
                                'Cheque Number': transaction_data[3],
                                'Transaction Remarks': ' '.join(transaction_data[4:-3]),
                                'Withdrawal Amount (INR)': transaction_data[-3],
                                'Deposit Amount (INR)': transaction_data[-2],
                                'Balance (INR)': transaction_data[-1]
                            }
                            if is_date(transaction['Transaction Date']) and is_amount(transaction['Balance (INR)']):
                                transactions.append(transaction)
                            else:
                                logging.warning(f"Skipping invalid last text transaction on page {page_num}: {transaction_data}")
                        except Exception as e:
                            logging.error(f"Error processing last text transaction on page {page_num}: {transaction_data}, Error: {e}")
    
    except Exception as e:
        logging.error(f"Failed to process PDF: {e}")
        return [], headers
    
    logging.info(f"Extracted {len(transactions)} transactions")
    return transactions, headers

def save_to_csv(transactions, headers, output_path):
    """Save extracted transactions to a CSV file."""
    if not transactions:
        logging.error("No transactions to save to CSV")
        return
    
    try:
        df = pd.DataFrame(transactions, columns=headers)
        
        # Clean data
        df['Value Date'] = pd.to_datetime(df['Value Date'], format='%d/%m/%Y', errors='coerce')
        df['Transaction Date'] = pd.to_datetime(df['Transaction Date'], format='%d/%m/%Y', errors='coerce')
        df['Withdrawal Amount (INR)'] = df['Withdrawal Amount (INR)'].replace('', '0.0').str.replace(',', '').astype(float)
        df['Deposit Amount (INR)'] = df['Deposit Amount (INR)'].replace('', '0.0').str.replace(',', '').astype(float)
        df['Balance (INR)'] = df['Balance (INR)'].str.replace(',', '').astype(float)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        logging.info(f"CSV file saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving CSV: {e}")

def main(pdf_path, output_path):
    """Main function to convert ICICI bank statement PDF to CSV."""
    logging.info(f"Starting PDF processing for {pdf_path}")
    transactions, headers = extract_transactions(pdf_path)
    if transactions:
        save_to_csv(transactions, headers, output_path)
    else:
        logging.error("No transactions found in the PDF.")

if __name__ == "__main__":
    # Example usage
    pdf_file = "/Users/karthiksagar/Expense-Classification/Statements/sbi1.pdf"  # Path to your PDF
    csv_file = "/Users/karthiksagar/Expense-Classification/sbi_statement.csv"  # Output CSV file
    main(pdf_file, csv_file)