import gradio as gr
import os
import openai

# Set API key
openai.api_key = os.getenv('OPENAI_API_KEY')

SAMPLE_SCHEMA = """
Table: customers
- customer_id (INT)
- customer_name (VARCHAR)
- email (VARCHAR)
- signup_date (DATE)

Table: orders
- order_id (INT)
- customer_id (INT)
- order_date (DATE)
- total_amount (DECIMAL)
- status (VARCHAR)

Table: products
- product_id (INT)
- product_name (VARCHAR)
- category (VARCHAR)
- price (DECIMAL)
"""

def generate_sql(user_question):
    try:
        prompt = f"""Given this database schema:

{SAMPLE_SCHEMA}

Convert this question to SQL query:
"{user_question}"

Rules:
- Return ONLY the SQL query, no explanations
- Use proper SQL syntax
- Be specific and accurate
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        return sql_query
    
    except Exception as e:
        return f"Error: {str(e)}"

# Example questions
examples = [
    ["Find all customers who signed up in 2024"],
    ["Show total revenue by product category"],
    ["Get top 10 customers by order count"],
    ["List all pending orders with customer names"],
]

# Build interface
with gr.Blocks(title="SQL Query Generator") as demo:
    gr.Markdown("# 🔍 Natural Language to SQL Generator")
    gr.Markdown("Ask questions about your data in plain English, get SQL queries instantly.")
    
    with gr.Row():
        with gr.Column():
            question_input = gr.Textbox(
                label="Your Question",
                placeholder="e.g., Show me customers who spent more than $1000",
                lines=3
            )
            generate_btn = gr.Button("Generate SQL", variant="primary")
        
        with gr.Column():
            sql_output = gr.Code(
                label="Generated SQL Query",
                language="sql",
                lines=10
            )
    
    gr.Markdown("### Example Questions")
    gr.Examples(
        examples=examples,
        inputs=question_input,
    )
    
    gr.Markdown("### Database Schema")
    gr.Code(SAMPLE_SCHEMA, language="sql", label="Available Tables")
    
    generate_btn.click(
        fn=generate_sql,
        inputs=question_input,
        outputs=sql_output
    )

if __name__ == "__main__":
    demo.launch()
    