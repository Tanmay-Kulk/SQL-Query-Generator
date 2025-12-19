import gradio as gr
import os
import sqlite3
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize in-memory database with sample data
def get_db_connection():
    """Create a new connection for each request"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT,
            email TEXT,
            signup_date DATE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date DATE,
            total_amount DECIMAL,
            status TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category TEXT,
            price DECIMAL
        )
    """)
    
    # Insert sample data - customers
    customers = [
        (1, 'John Smith', 'john@email.com', '2024-01-15'),
        (2, 'Sarah Johnson', 'sarah@email.com', '2024-02-20'),
        (3, 'Mike Brown', 'mike@email.com', '2023-11-10'),
        (4, 'Emily Davis', 'emily@email.com', '2024-03-05'),
        (5, 'David Wilson', 'david@email.com', '2023-12-01'),
    ]
    cursor.executemany('INSERT INTO customers VALUES (?,?,?,?)', customers)
    
    # Insert sample data - products
    products = [
        (1, 'Laptop Pro', 'Electronics', 1299.99),
        (2, 'Wireless Mouse', 'Electronics', 29.99),
        (3, 'Office Chair', 'Furniture', 249.99),
        (4, 'Desk Lamp', 'Furniture', 49.99),
        (5, 'USB Cable', 'Electronics', 9.99),
        (6, 'Monitor 27"', 'Electronics', 399.99),
        (7, 'Keyboard Mechanical', 'Electronics', 89.99),
        (8, 'Standing Desk', 'Furniture', 499.99),
    ]
    cursor.executemany('INSERT INTO products VALUES (?,?,?,?)', products)
    
    # Insert sample data - orders
    orders = [
        (1, 1, '2024-01-20', 1329.98, 'Completed'),
        (2, 2, '2024-02-25', 249.99, 'Completed'),
        (3, 1, '2024-03-10', 399.99, 'Completed'),
        (4, 3, '2024-03-15', 559.97, 'Pending'),
        (5, 4, '2024-03-20', 1299.99, 'Completed'),
        (6, 2, '2024-04-01', 89.99, 'Shipped'),
        (7, 5, '2024-04-05', 499.98, 'Completed'),
        (8, 1, '2024-04-10', 29.99, 'Pending'),
        (9, 3, '2024-04-12', 49.99, 'Completed'),
        (10, 4, '2024-04-15', 1699.97, 'Shipped'),
    ]
    cursor.executemany('INSERT INTO orders VALUES (?,?,?,?,?)', orders)
    
    conn.commit()
    return conn


SCHEMA_INFO = """
Table: customers (5 records)
- customer_id (INT)
- customer_name (TEXT)
- email (TEXT)
- signup_date (DATE)

Table: orders (10 records)
- order_id (INT)
- customer_id (INT)
- order_date (DATE)
- total_amount (DECIMAL)
- status (TEXT: Completed, Pending, Shipped)

Table: products (8 records)
- product_id (INT)
- product_name (TEXT)
- category (TEXT: Electronics, Furniture)
- price (DECIMAL)
"""

def generate_and_execute_sql(user_question):
    try:
        # Generate SQL query
        prompt = f"""Given this database schema:

{SCHEMA_INFO}

Convert this question to a SQL query:
"{user_question}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Be specific and accurate
- Use JOIN when querying multiple tables
"""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Create fresh connection for each query
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        # Format results
        if results:
            result_text = "Query Results:\n\n"
            result_text += " | ".join(columns) + "\n"
            result_text += "-" * (len(" | ".join(columns))) + "\n"
            for row in results:
                result_text += " | ".join(str(val) for val in row) + "\n"
        else:
            result_text = "Query executed successfully. No results returned."
        
        conn.close()  # Clean up
        return sql_query, result_text
        
    except sqlite3.Error as e:
        return sql_query if 'sql_query' in locals() else "Error generating query", f"SQL Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}", ""

# Example questions
examples = [
    ["Show all customers"],
    ["Find total revenue by customer"],
    ["List all electronics products under $100"],
    ["Show pending orders with customer names"],
    ["What's the most expensive product?"],
    ["Count orders by status"],
]

# Build interface
with gr.Blocks(title="SQL Query Generator & Executor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔍 Natural Language to SQL Generator")
    gr.Markdown("Ask questions in plain English. Get SQL queries AND see real results from sample data.")
    
    with gr.Row():
        question_input = gr.Textbox(
            label="Your Question",
            placeholder="e.g., Show me customers who placed orders in 2024",
            lines=2,
            scale=3
        )
        generate_btn = gr.Button("Generate & Execute", variant="primary", scale=1)
    
    with gr.Row():
        with gr.Column():
            sql_output = gr.Code(
                label="Generated SQL Query",
                language="sql",
                lines=8
            )
        
        with gr.Column():
            results_output = gr.Textbox(
                label="Query Results",
                lines=8,
                max_lines=15
            )
    
    gr.Markdown("### Try These Examples")
    gr.Examples(
        examples=examples,
        inputs=question_input,
    )
    
    with gr.Accordion("📊 Sample Database Schema & Data", open=False):
        gr.Markdown(SCHEMA_INFO)
        gr.Markdown("""
        **Sample Data Preview:**
        - 5 customers (John Smith, Sarah Johnson, Mike Brown, Emily Davis, David Wilson)
        - 8 products across Electronics and Furniture categories
        - 10 orders with various statuses (Completed, Pending, Shipped)
        - Orders range from $29.99 to $1,699.97
        - Data spans from Nov 2023 to Apr 2024
        """)
    
    generate_btn.click(
        fn=generate_and_execute_sql,
        inputs=question_input,
        outputs=[sql_output, results_output]
    )

if __name__ == "__main__":
    demo.launch()