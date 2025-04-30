FROM python:3.12-slim

WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install  -r requirements.txt

# Copy other necessary files
COPY dataset/main_faq_database.json /app/dataset/main_faq_database.json
COPY menu_assistant .

# Expose port for Streamlit
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "menu_assistant/app.py"]
