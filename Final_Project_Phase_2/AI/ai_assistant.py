import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class AIChatAssistant:
    def __init__(self):
        try:
            from openai import OpenAI
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "The OpenAI package is not installed. Run: pip install openai"
            ) from exc

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            try:
                api_key = st.secrets.get("OPENAI_API_KEY")
            except Exception:
                api_key = None

        if not api_key:
            raise RuntimeError("OpenAI API key was not found.")

        self.client = OpenAI(api_key=api_key)

    def build_prompt(self, app_context):
        return (
            "You are an AI assistant for the Horizon Electric Vehicles app. "
            "Help users answer simple questions about inventory, vehicles, orders, "
            "and app guidance. Use the app context when it is useful. "
            f"App context: {app_context}"
        )

    def generate_response(self, user_question, app_context):
        messages = [
            {
                "role": "system",
                "content": self.build_prompt(app_context)
            },
            {
                "role": "user",
                "content": user_question
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages
        )

        return response.choices[0].message.content
