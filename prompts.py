# prompts.py

PLAN_PROMPT = """
<<<<<<< HEAD
You are an expert Python developer specializing in financial data extraction from PDF documents.
Your goal is to create a plan to write a Python parser for a given bank statement PDF.

The parser must be a single function `parse(pdf_path: str) -> pd.DataFrame` that extracts all transactions.

**CONTEXT:**
1.  **PDF Text Snippet**: Here is the raw text extracted from the first page of the PDF. This will help you understand the document's structure.
    ```text
    {pdf_text}
    ```

2.  **Target Schema**: The output DataFrame must exactly match this schema (columns and dtypes).
    ```
    {schema}
    ```

**TASK:**
Create a concise, step-by-step plan to write the Python parser. Focus on:
- **Library Choice**: Specify which library to use (e.g., `pdfplumber`).
- **Transaction Identification**: How to locate the start of the transaction table and identify transaction rows.
- **Data Extraction**: The logic for extracting each required field (`Date`, `Transaction Particulars`, `Debit`, `Credit`, `Balance`) from a single transaction line. Mention if you'll use regex, string splitting, or another method.
- **Data Cleaning**: How to handle potential data type issues, especially for dates and numeric columns.

**PREVIOUS ATTEMPT FEEDBACK (if any):**
{error_feedback}

Your plan should be clear and actionable for a code generation model to follow.
c3dcd4e (Implement self-correcting agent with Groq API)
"""

CODE_GENERATION_PROMPT = """
You are a Python code generation expert. Based on the provided plan, write the complete, executable Python code for the bank statement parser.

**PLAN:**
{plan}

**TASK:**
- Write a single Python script.
- The script must contain all necessary imports (`pandas`, `pdfplumber`, `re`, etc.).
- The script must define a function with the exact signature: `parse(pdf_path: str) -> pd.DataFrame`.
- The function should return a pandas DataFrame conforming to the plan.
- **Do not include any explanations, comments, or any text other than the Python code itself.**

**STRICT REQUIREMENTS:**
- The final output must be only the raw Python code. Do not wrap it in markdown backticks or any other formatting.
<<<<<<< HEAD
- Ensure numeric columns (`Debit`, `Credit`, `Balance`) are converted to floats and nulls are handled correctly (e.g., filled with 0.0).
- Ensure the 'Date' column is converted to datetime objects.
"""
