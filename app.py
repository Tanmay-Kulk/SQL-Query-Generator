import gradio as gr
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Sample data stored as dictionaries (no database)
CUSTOMERS = [
    {"customer_id": 1, "customer_name": "John Smith", "email": "john@email.com", "signup_date": "2024-01-15"},
    {"customer_id": 2, "customer_name": "Sarah Johnson", "email": "sarah@email.com", "signup_date": "2024-02-20"},
    {"customer_id": 3, "customer_name": "Mike Brown", "email": "mike@email.com", "signup_date": "2023-11-10"},
    {"customer_id": 4, "customer_name": "Emily Davis", "email": "emily@email.com", "signup_date": "2024-03-05"},
    {"customer_id": 5, "customer_name": "David Wilson", "email": "david@email.com", "signup_date": "2023-12-01"},
]

PRODUCTS = [
    {"product_id": 1, "product_name": "Laptop Pro", "category": "Electronics", "price": 1299.99},
    {"product_id": 2, "product_name": "Wireless Mouse", "category": "Electronics", "price": 29.99},
    {"product_id": 3, "product_name": "Office Chair", "category": "Furniture", "price": 249.99},
    {"product_id": 4, "product_name": "Desk Lamp", "category": "Furniture", "price": 49.99},
    {"product_id": 5, "product_name": "USB Cable", "category": "Electronics", "price": 9.99},
    {"product_id": 6, "product_name": "Monitor 27\"", "category": "Electronics", "price": 399.99},
    {"product_id": 7, "product_name": "Keyboard Mechanical", "category": "Electronics", "price": 89.99},
    {"product_id": 8, "product_name": "Standing Desk", "category": "Furniture", "price": 499.99},
]

ORDERS = [
    {"order_id": 1, "customer_id": 1, "order_date": "2024-01-20", "total_amount": 1329.98, "status": "Completed"},
    {"order_id": 2, "customer_id": 2, "order_date": "2024-02-25", "total_amount": 249.99, "status": "Completed"},
    {"order_id": 3, "customer_id": 1, "order_date": "2024-03-10", "total_amount": 399.99, "status": "Completed"},
    {"order_id": 4, "customer_id": 3, "order_date": "2024-03-15", "total_amount": 559.97, "status": "Pending"},
    {"order_id": 5, "customer_id": 4, "order_date": "2024-03-20", "total_amount": 1299.99, "status": "Completed"},
    {"order_id": 6, "customer_id": 2, "order_date": "2024-04-01", "total_amount": 89.99, "status": "Shipped"},
    {"order_id": 7, "customer_id": 5, "order_date": "2024-04-05", "total_amount": 499.98, "status": "Completed"},
    {"order_id": 8, "customer_id": 1, "order_date": "2024-04-10", "total_amount": 29.99, "status": "Pending"},
    {"order_id": 9, "customer_id": 3, "order_date": "2024-04-12", "total_amount": 49.99, "status": "Completed"},
    {"order_id": 10, "customer_id": 4, "order_date": "2024-04-15", "total_amount": 1699.97, "status": "Shipped"},
]

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

def generate_sql(user_question):
    """Generate SQL query from natural language"""
    try:
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
        
        # Show sample data based on query
        sample_results = get_sample_results(sql_query.lower())
        
        return sql_query, sample_results
        
    except Exception as e:
        return f"Error: {str(e)}", ""

def get_sample_results(query):
    """Return sample data based on query keywords"""
    
    if "customer" in query and "order" not in query:
        result = "Sample Results:\n\n"
        result += "customer_id | customer_name | email | signup_date\n"
        result += "-" * 70 + "\n"
        for c in CUSTOMERS[:3]:
            result += f"{c['customer_id']} | {c['customer_name']} | {c['email']} | {c['signup_date']}\n"
        result += f"\n(Showing 3 of {len(CUSTOMERS)} customers)"
        return result
    
    elif "product" in query:
        result = "Sample Results:\n\n"
        result += "product_id | product_name | category | price\n"
        result += "-" * 60 + "\n"
        for p in PRODUCTS[:4]:
            result += f"{p['product_id']} | {p['product_name']} | {p['category']} | ${p['price']}\n"
        result += f"\n(Showing 4 of {len(PRODUCTS)} products)"
        return result
    
    elif "order" in query:
        result = "Sample Results:\n\n"
        result += "order_id | customer_id | order_date | total_amount | status\n"
        result += "-" * 70 + "\n"
        for o in ORDERS[:5]:
            result += f"{o['order_id']} | {o['customer_id']} | {o['order_date']} | ${o['total_amount']} | {o['status']}\n"
        result += f"\n(Showing 5 of {len(ORDERS)} orders)"
        return result
    
    elif "sum" in query or "total" in query or "revenue" in query:
        total = sum(o['total_amount'] for o in ORDERS)
        return f"Sample Results:\n\ntotal_revenue\n---------\n${total:.2f}"
    
    elif "count" in query:
        return f"Sample Results:\n\ncount\n-----\n{len(ORDERS)}"
    
    else:
        return "Sample Results:\n\n(Query generated successfully. Results would appear here with actual database.)"

# Example questions
examples = [
    ["Show all customers"],
    ["Find total revenue"],
    ["List all electronics products"],
    ["Show pending orders"],
    ["What's the most expensive product?"],
    ["Count orders by status"],
]

# Build interface
with gr.Blocks(title="SQL Query Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔍 Natural Language to SQL Generator")
    gr.Markdown("Ask questions in plain English and get SQL queries instantly. Sample results shown below.")
    
    with gr.Row():
        question_input = gr.Textbox(
            label="Your Question",
            placeholder="e.g., Show me customers who placed orders in 2024",
            lines=2,
            scale=3
        )
        generate_btn = gr.Button("Generate SQL", variant="primary", scale=1)
    
    with gr.Row():
        with gr.Column():
            sql_output = gr.Code(
                label="Generated SQL Query",
                language="sql",
                lines=8
            )
        
        with gr.Column():
            results_output = gr.Textbox(
                label="Sample Results Preview",
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
        fn=generate_sql,
        inputs=question_input,
        outputs=[sql_output, results_output]
    )

if __name__ == "__main__":
    demo.launch()