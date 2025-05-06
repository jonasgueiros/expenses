import sqlite3
import flet as ft
from transformers import pipeline

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

# Set up the Hugging Face Transformers pipeline
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

# Function to query the SQLite database
def query_database(query):
    conn = sqlite3.connect('expenses_db.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Function to generate a response using the Hugging Face Transformers pipeline
def generate_response(prompt):
    # Example context from the database
    context = "The database contains information about expenses, including descriptions, amounts, and dates."
    result = list(qa_pipeline(inputs={"question": prompt, "context": context}))[0]
    return result['answer']

class AIChat(ft.UserControl):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.create_widgets()

    def build(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    self.chat_display,
                    self.user_input,
                    ft.ElevatedButton("Send", on_click=self.handle_query)
                ]
            ),
            bgcolor=ft.colors.WHITE,
            padding=20,
            width=400,
            height=600
        )

    def create_widgets(self):
        self.chat_display = ft.TextField(
            label="Chat",
            multiline=True,
            read_only=True,
            expand=True
        )
        self.user_input = ft.TextField(label="Your Query")

    def handle_query(self, e):
        user_query = self.user_input.value
        if self.chat_display.value is None:
            self.chat_display.value = ""
        self.chat_display.value += f"User: {user_query}\n"

        # Generate response using the Hugging Face Transformers pipeline
        response = generate_response(user_query)
        self.chat_display.value += f"AI: {response}\n"

        self.user_input.value = ""
        if self.page:
            self.page.update()

def main(page: ft.Page):
    ai_chat = AIChat(page)
    page.add(ai_chat)

ft.app(target=main)