import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppresses INFO and WARNING messages
import requests
from transformers import pipeline
import tkinter as tk
from tkinter import scrolledtext, messagebox
from PIL import Image, ImageTk

# Set up NewsAPI parameters
NEWS_API_KEY = '90fd633891a048419fe41234cbd3b568'  # Replace with your actual NewsAPI key
NEWS_API_ENDPOINT = 'https://newsapi.org/v2/everything'

def get_news_articles(query, api_key=NEWS_API_KEY):
    """
    Function to get news articles based on user query
    """
    params = {
        'q': query,
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 5  # Fetch top 5 articles
    }
    
    response = requests.get(NEWS_API_ENDPOINT, params=params)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        print("Error fetching news:", response.status_code)
        return []

def summarize_article(article_content):
    """
    Use a transformer model to summarize a given article
    """
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    
    # Calculate a reasonable max_length based on input length
    input_length = len(article_content.split())
    
    if input_length < 5:
        return "Content too short to summarize."

    # Adjust max_length dynamically based on input length
    max_length = min(50, input_length // 2)  # Set max_length to half the input length or 50
    min_length = max(5, input_length // 4)   # Ensure a minimum length for the summary

    # Summarize article
    summary = summarizer(article_content, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def fetch_and_summarize():
    """
    Fetch news articles and display summaries in the text area
    """
    user_query = entry.get()
    if not user_query:
        messagebox.showwarning("Input Error", "Please enter a topic.")
        return
    
    articles = get_news_articles(user_query)
    
    # Clear previous output
    output_text.delete(1.0, tk.END)
    
    if articles:
        output_text.insert(tk.END, f"Found {len(articles)} articles about '{user_query}'. Here are the summaries:\n\n")
        
        for idx, article in enumerate(articles, 1):
            title = article['title']
            content = article.get('content', '')
            
            if content:
                summary = summarize_article(content)
                output_text.insert(tk.END, f"Article {idx}: {title}\n")
                output_text.insert(tk.END, "Summary: " + summary + "\n\n")
            else:
                output_text.insert(tk.END, f"Article {idx}: {title}\n")
                output_text.insert(tk.END, "No content available for summarization.\n\n")
    else:
        output_text.insert(tk.END, f"No articles found for '{user_query}'.\n")

def clear_input():
    """
    Clear the input and output areas
    """
    entry.delete(0, tk.END)  # Clear input field
    output_text.delete(1.0, tk.END)  # Clear output text area

def make_draggable(widget):
    """
    Make the given widget draggable.
    """
    def on_drag(event):
        x = window.winfo_pointerx() - offset_x
        y = window.winfo_pointery() - offset_y
        widget.place(x=x, y=y)

    def on_button_press(event):
        global offset_x, offset_y
        offset_x = event.x
        offset_y = event.y

    widget.bind("<ButtonPress-1>", on_button_press)
    widget.bind("<B1-Motion>", on_drag)

# Create the main window
window = tk.Tk()
window.title("News Aggregator and Summarizer")
window.geometry("1600x900")  # Set window size

# Set the background image
bg_image = Image.open("Breaking.jpg")  # Make sure this matches your uploaded image file name
bg_image = bg_image.resize((1600,900), Image.LANCZOS)  # Resize the image
bg_photo = ImageTk.PhotoImage(bg_image)

# Create a canvas to place the background image
canvas = tk.Canvas(window, width=1366, height=768)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, anchor="nw", image=bg_photo)

# Create a frame for the label to allow for adjustable size
label_frame = tk.Frame(window, bg='white')
label_frame.place(relx=0.5, y=20, anchor='n', relwidth=0.6)

# Create and place the input label inside the label frame
label = tk.Label(label_frame, text="Enter a topic to get the latest news:", bg='white', font=("Arial", 12))
label.pack(fill='both')  # Allow the label to expand and fill the frame

entry = tk.Entry(window, width=50, font=("Arial", 12))
entry.place(relx=0.5, y=80, anchor='n')

# Create and place the fetch button
fetch_button = tk.Button(window, text="Fetch and Summarize", command=fetch_and_summarize, font=("Arial", 12))
fetch_button.place(relx=0.5, y=120, anchor='n')

# Create and place the clear button
clear_button = tk.Button(window, text="Clear", command=clear_input, font=("Arial", 12))
clear_button.place(relx=0.5, y=160, anchor='n')

# Create a frame for the output text area
output_frame = tk.Frame(window, bg='lightblue', bd=2, relief='solid')
output_frame.place(relx=0.5, y=210, anchor='n', relwidth=0.6, relheight=0.4)

# Title bar for the output frame
title_bar = tk.Frame(output_frame, bg='darkblue', relief='flat')
title_bar.pack(fill='x')

# Custom close button
close_button = tk.Button(title_bar, text='X', command=window.quit, bg='red', fg='white', bd=0)
close_button.pack(side='right')

# Custom minimize button
minimize_button = tk.Button(title_bar, text='–', command=lambda: output_frame.withdraw(), bg='lightgrey', fg='black', bd=0)
minimize_button.pack(side='right')

# Custom maximize button
maximized = False  # Track the state of maximization

def toggle_maximize():
    global maximized
    if maximized:
        output_frame.place(relwidth=0.6, relheight=0.4)  # Restore original size
        maximize_button.config(text='⬜')  # Change button text to maximize
    else:
        output_frame.place(relwidth=1, relheight=1)  # Maximize
        maximize_button.config(text='⬛')  # Change button text to minimize
    maximized = not maximized

maximize_button = tk.Button(title_bar, text='⬜', command=toggle_maximize, bg='lightgrey', fg='black', bd=0)
maximize_button.pack(side='right')

# Create and place the output text area inside the frame
output_text = scrolledtext.ScrolledText(output_frame, font=("Arial", 12), bg='#DDEEFF', fg='black', bd=0)
output_text.pack(expand=True, fill='both')  # Allow the text area to expand and fill the frame

# Make the output frame draggable
make_draggable(output_frame)

# Make the label frame draggable
make_draggable(label_frame)

# Start the GUI event loop
window.mainloop()
