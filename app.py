import gradio as gr
import os
import sqlite3
import openai

# Set API key with strip to avoid whitespace issues
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    openai.api_key = api_key.strip()

def create_sample_database():
    """Create a properly designed database with foreign keys and realistic data"""
    conn = sqlite3.connect(':memory:')
    
    # CRITICAL: Enable foreign key support in SQLite
    conn.execute("PRAGMA foreign_keys = ON")
    
    cursor = conn.cursor()
    
    # Create customers table (parent table)
    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            signup_date DATE NOT NULL,
            city TEXT,
            state TEXT
        )
    """)
    
    # Create products table (independent table)
    cursor.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price DECIMAL(10,2) NOT NULL CHECK(price >= 0),
            stock_quantity INTEGER DEFAULT 0
        )
    """)
    
    # Create orders table (child of customers)
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date DATE NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL CHECK(total_amount >= 0),
            status TEXT NOT NULL CHECK(status IN ('Pending', 'Shipped', 'Completed', 'Cancelled')),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """)
    
    # Create order_items table (junction table - many-to-many between orders and products)
    cursor.execute("""
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price DECIMAL(10,2) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
        )
    """)
    
    # Insert sample customers
    customers = [
        ('John Smith', 'john@email.com', '2024-01-15', 'Boston', 'MA'),
        ('Sarah Johnson', 'sarah@email.com', '2024-02-20', 'New York', 'NY'),
        ('Mike Brown', 'mike@email.com', '2023-11-10', 'Chicago', 'IL'),
        ('Emily Davis', 'emily@email.com', '2024-03-05', 'San Francisco', 'CA'),
        ('David Wilson', 'david@email.com', '2023-12-01', 'Seattle', 'WA'),
        ('Lisa Anderson', 'lisa@email.com', '2024-01-08', 'Boston', 'MA'),
        ('Robert Taylor', 'robert@email.com', '2023-10-15', 'Austin', 'TX'),
    ]
    cursor.executemany(
        'INSERT INTO customers (customer_name, email, signup_date, city, state) VALUES (?,?,?,?,?)', 
        customers
    )
    
    # Insert sample products
    products = [
        ('Laptop Pro 15"', 'Electronics', 1299.99, 25),
        ('Wireless Mouse', 'Electronics', 29.99, 150),
        ('Office Chair Executive', 'Furniture', 249.99, 40),
        ('Desk Lamp LED', 'Furniture', 49.99, 80),
        ('USB-C Cable 6ft', 'Electronics', 9.99, 200),
        ('Monitor 27" 4K', 'Electronics', 399.99, 35),
        ('Keyboard Mechanical RGB', 'Electronics', 89.99, 60),
        ('Standing Desk Electric', 'Furniture', 499.99, 15),
        ('Webcam HD 1080p', 'Electronics', 79.99, 45),
        ('Headphones Wireless', 'Electronics', 149.99, 70),
        ('Desk Mat Large', 'Furniture', 24.99, 100),
        ('Phone Stand Adjustable', 'Electronics', 19.99, 120),
    ]
    cursor.executemany(
        'INSERT INTO products (product_name, category, price, stock_quantity) VALUES (?,?,?,?)', 
        products
    )
    
    # Insert orders WITHOUT total_amount (we'll calculate it)
    orders = [
        (1, '2024-01-20', 0, 'Completed'),    # John Smith
        (2, '2024-02-25', 0, 'Completed'),    # Sarah Johnson
        (1, '2024-03-10', 0, 'Completed'),    # John Smith
        (3, '2024-03-15', 0, 'Pending'),      # Mike Brown
        (4, '2024-03-20', 0, 'Completed'),    # Emily Davis
        (2, '2024-04-01', 0, 'Shipped'),      # Sarah Johnson
        (5, '2024-04-05', 0, 'Completed'),    # David Wilson
        (1, '2024-04-10', 0, 'Pending'),      # John Smith
        (3, '2024-04-12', 0, 'Completed'),    # Mike Brown
        (4, '2024-04-15', 0, 'Shipped'),      # Emily Davis
        (6, '2024-04-18', 0, 'Completed'),    # Lisa Anderson
        (7, '2024-04-20', 0, 'Pending'),      # Robert Taylor
    ]
    cursor.executemany(
        'INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?,?,?,?)', 
        orders
    )
    
    # Insert order items (product_id, quantity, unit_price from products table)
    order_items = [
        # Order 1: John Smith - Laptop + Mouse + Keyboard
        (1, 1, 1, 1299.99),  # Laptop
        (1, 2, 1, 29.99),    # Mouse
        (1, 7, 1, 89.99),    # Keyboard
        # Total: 1419.97
        
        # Order 2: Sarah Johnson - Office Chair
        (2, 3, 1, 249.99),
        # Total: 249.99
        
        # Order 3: John Smith - Monitor
        (3, 6, 1, 399.99),
        # Total: 399.99
        
        # Order 4: Mike Brown - Standing Desk + USB Cables
        (4, 8, 1, 499.99),
        (4, 5, 6, 9.99),     # 6 USB cables @ 9.99 each = 59.94
        # Total: 559.93
        
        # Order 5: Emily Davis - Laptop
        (5, 1, 1, 1299.99),
        # Total: 1299.99
        
        # Order 6: Sarah Johnson - Headphones + Keyboard
        (6, 10, 1, 149.99),
        (6, 7, 1, 89.99),
        # Total: 239.98
        
        # Order 7: David Wilson - Standing Desk
        (7, 8, 1, 499.99),
        # Total: 499.99
        
        # Order 8: John Smith - Mouse
        (8, 2, 1, 29.99),
        # Total: 29.99
        
        # Order 9: Mike Brown - Desk Lamp
        (9, 4, 1, 49.99),
        # Total: 49.99
        
        # Order 10: Emily Davis - Laptop + Monitor + Desk Mats
        (10, 1, 1, 1299.99),
        (10, 6, 1, 399.99),
        (10, 11, 6, 24.99),  # 6 desk mats @ 24.99 each = 149.94
        # Total: 1849.92
        
        # Order 11: Lisa Anderson - Webcam + Headphones + Phone Stands
        (11, 9, 1, 79.99),
        (11, 10, 1, 149.99),
        (11, 12, 5, 19.99),  # 5 phone stands @ 19.99 each = 99.95
        # Total: 329.93
        
        # Order 12: Robert Taylor - Webcam
        (12, 9, 1, 79.99),
        # Total: 79.99
    ]
    cursor.executemany(
        'INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?,?,?,?)', 
        order_items
    )
    
    # NOW calculate and update the correct total_amount for each order
    cursor.execute("""
        UPDATE orders
        SET total_amount = (
            SELECT SUM(quantity * unit_price)
            FROM order_items
            WHERE order_items.order_id = orders.order_id
        )
    """)
    
    conn.commit()
    return conn

SCHEMA_INFO = """
Table: customers (7 records)
- customer_id INTEGER PRIMARY KEY
- customer_name TEXT NOT NULL
- email TEXT UNIQUE NOT NULL
- signup_date DATE NOT NULL
- city TEXT
- state TEXT

Table: products (12 records)
- product_id INTEGER PRIMARY KEY
- product_name TEXT NOT NULL
- category TEXT NOT NULL (Electronics, Furniture)
- price DECIMAL(10,2) NOT NULL
- stock_quantity INTEGER

Table: orders (12 records)
- order_id INTEGER PRIMARY KEY
- customer_id INTEGER NOT NULL → REFERENCES customers(customer_id)
- order_date DATE NOT NULL
- total_amount DECIMAL(10,2) NOT NULL (calculated from order_items)
- status TEXT NOT NULL (Pending, Shipped, Completed, Cancelled)

Table: order_items (23 records - junction table)
- order_item_id INTEGER PRIMARY KEY
- order_id INTEGER NOT NULL → REFERENCES orders(order_id)
- product_id INTEGER NOT NULL → REFERENCES products(product_id)
- quantity INTEGER NOT NULL
- unit_price DECIMAL(10,2) NOT NULL

Relationships:
- One customer can have many orders (1:N)
- One order can have many order_items (1:N)
- One product can appear in many order_items (1:N)
- orders.total_amount = SUM(order_items.quantity × order_items.unit_price) for that order
- orders.customer_id → customers.customer_id (CASCADE on delete/update)
- order_items.order_id → orders.order_id (CASCADE on delete/update)
- order_items.product_id → products.product_id (RESTRICT on delete)
"""

def generate_and_execute_sql(user_question):
    try:
        # Generate SQL query
        prompt = f"""Given this database schema with foreign keys:

{SCHEMA_INFO}

Convert this question to a SQL query:
"{user_question}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQLite syntax
- Use JOINs when querying related tables
- Be specific and accurate
- Use aggregate functions (SUM, COUNT, AVG) when appropriate
- For questions about "which customer", "which product", join to get names not just IDs
- The total_amount in orders equals SUM(quantity * unit_price) from order_items
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=300
        )
        
        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Create fresh database and execute query
        conn = create_sample_database()
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # Format results
        if results:
            result_text = "Query Results:\n\n"
            result_text += " | ".join(columns) + "\n"
            result_text += "-" * min(100, len(" | ".join(columns)) + 20) + "\n"
            for row in results[:50]:  # Limit to 50 rows for display
                result_text += " | ".join(str(val) if val is not None else "NULL" for val in row) + "\n"
            
            if len(results) > 50:
                result_text += f"\n... ({len(results) - 50} more rows not shown)"
            result_text += f"\n({len(results)} row{'s' if len(results) != 1 else ''} total)"
        else:
            result_text = "Query executed successfully. No results returned."
        
        conn.close()
        return sql_query, result_text
        
    except sqlite3.Error as e:
        return sql_query if 'sql_query' in locals() else "Error generating query", f"SQL Error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}", ""

# Example questions - now with more complex queries
examples = [
    ["Show all customers from Boston"],
    ["Find total revenue by product category"],
    ["Which customer has spent the most money?"],
    ["List all products that were ordered more than once"],
    ["Show pending orders with customer names and order totals"],
    ["What's the average order value?"],
    ["Which products are low in stock (less than 30 units)?"],
    ["Show all orders from customers in California"],
    ["Find the total quantity sold for each product"],
    ["Verify that order totals match the sum of their items"],
]

# Build interface
with gr.Blocks(title="SQL Query Generator & Executor", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔍 Natural Language to SQL Generator")
    gr.Markdown("Ask complex questions about relational data. Generates SQL with proper JOINs and executes on sample database with accurate calculations.")
    
    with gr.Row():
        question_input = gr.Textbox(
            label="Your Question",
            placeholder="e.g., Which customers ordered laptops in 2024?",
            lines=2,
            scale=3
        )
        generate_btn = gr.Button("Generate & Execute", variant="primary", scale=1)
    
    with gr.Row():
        with gr.Column():
            sql_output = gr.Code(
                label="Generated SQL Query",
                language="sql",
                lines=10
            )
        
        with gr.Column():
            results_output = gr.Textbox(
                label="Query Results",
                lines=10,
                max_lines=20
            )
    
    gr.Markdown("### Try These Complex Examples")
    gr.Examples(
        examples=examples,
        inputs=question_input,
    )
    
    with gr.Accordion("📊 Database Schema with Foreign Keys", open=False):
        gr.Code(SCHEMA_INFO, language="text", label="Complete Schema")
        gr.Markdown("""
        **Sample Data Summary:**
        - 7 customers across 6 US cities
        - 12 products (Electronics & Furniture)
        - 12 orders with various statuses
        - 23 order items (individual products within orders)
        - All order totals are calculated accurately from order items
        
        **Foreign Key Relationships:**
        - Orders belong to Customers (customer_id)
        - Order Items belong to Orders (order_id)
        - Order Items reference Products (product_id)
        
        **Data Integrity:**
        - orders.total_amount = SUM(order_items.quantity × unit_price)
        - Foreign keys enforced with CASCADE/RESTRICT
        - CHECK constraints on prices, quantities, status values
        
        **Supports Complex Queries:**
        - Multi-table JOINs (3-4 tables)
        - Aggregate functions (SUM, COUNT, AVG)
        - GROUP BY and HAVING clauses
        - Subqueries and CTEs
        - Data validation queries
        """)
    
    generate_btn.click(
        fn=generate_and_execute_sql,
        inputs=question_input,
        outputs=[sql_output, results_output]
    )

if __name__ == "__main__":
    demo.launch()