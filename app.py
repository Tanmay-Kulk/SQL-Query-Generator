import gradio as gr
import os
import openai

# Debug: Check what the key looks like
api_key = os.getenv("OPENAI_API_KEY")

def generate_sql(user_question):
    try:
        # Additional debug info
        if not api_key:
            return "Error: API key not found in environment"
        
        if not api_key.startswith("sk-"):
            return f"Error: API key doesn't start with 'sk-'. It starts with: '{api_key[:10]}...'"
        
        # Check for hidden characters
        key_len = len(api_key)
        if key_len < 20:
            return f"Error: API key too short ({key_len} chars). Should be 48+ characters"
        
        # Set the key
        openai.api_key = api_key.strip()  # Strip any whitespace
        
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
            temperature=0,
            max_tokens=200
        )
        
        sql_query = response.choices[0].message.content.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        return sql_query
    
    except Exception as e:
        return f"Error: {str(e)}\n\nKey length: {len(api_key) if api_key else 0}\nKey starts with: {api_key[:15] if api_key else 'None'}..."

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