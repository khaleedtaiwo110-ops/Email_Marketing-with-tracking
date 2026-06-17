import tkinter as tk
from tkinter import ttk, messagebox
import requests
import feedparser
import threading

# -------------------------------
# CONFIG
# -------------------------------

TRAVEL_KEYWORDS = {
    "site visit": 15,
    "field work": 20,
    "on-site": 15,
    "deployment": 10,
    "offshore": 20,
    "project site": 15,
    "multi-location": 20,
    "international": 25,
    "travel required": 30,
    "business trip": 15,
    "expansion": 10,
    "operations across": 20,
    "remote": -20
}

MAX_SCORE = 100


# -------------------------------
# DATA FETCHING
# -------------------------------

def fetch_news(company_name):
    url = f"https://news.google.com/rss/search?q={company_name}"
    feed = feedparser.parse(url)
    return feed.entries[:15]


# -------------------------------
# ANALYSIS ENGINE
# -------------------------------

def analyze_company(company_name):
    entries = fetch_news(company_name)

    score = 0
    reasons = []
    matched_keywords = set()

    for entry in entries:
        text = (entry.title + " " + entry.summary).lower()

        for keyword, weight in TRAVEL_KEYWORDS.items():
            if keyword in text and keyword not in matched_keywords:
                score += weight
                matched_keywords.add(keyword)
                reasons.append(f"Detected '{keyword}' (+{weight})")

    # Normalize score
    score = max(0, min(score, MAX_SCORE))

    # Confidence logic
    if score >= 70:
        confidence = "High"
    elif score >= 40:
        confidence = "Medium"
    else:
        confidence = "Low"

    return score, confidence, reasons


# -------------------------------
# UI LOGIC
# -------------------------------

def run_analysis():
    company = company_entry.get().strip()

    if not company:
        messagebox.showerror("Error", "Please enter a company name")
        return

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, "Analyzing... Please wait...\n")

    def task():
        try:
            score, confidence, reasons = analyze_company(company)

            output = f"Company: {company}\n"
            output += f"\nTravel Likelihood: {score}%"
            output += f"\nConfidence Level: {confidence}\n\n"
            output += "Key Signals Detected:\n"

            if reasons:
                for r in reasons[:8]:
                    output += f"• {r}\n"
            else:
                output += "• No strong travel indicators found\n"

            output += "\nInsight:\n"
            if score >= 70:
                output += "This company likely has frequent project-based travel."
            elif score >= 40:
                output += "This company shows moderate travel activity."
            else:
                output += "This company likely has minimal travel needs."

            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, output)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=task, daemon=True).start()


def clear_results():
    result_text.delete(1.0, tk.END)
    company_entry.delete(0, tk.END)




# -------------------------------
# UI DESIGN
# -------------------------------

root = tk.Tk()
root.title("Company Travel Analyzer")
root.geometry("600x500")
root.configure(bg="#f4f6f8")

# Title
title_label = tk.Label(root, text="Company Travel Analyzer",
                       font=("Arial", 18, "bold"), bg="#f4f6f8")
title_label.pack(pady=10)

# Input Frame
input_frame = tk.Frame(root, bg="#f4f6f8")
input_frame.pack(pady=10)

company_entry = tk.Entry(input_frame, width=40, font=("Arial", 12))
company_entry.grid(row=0, column=0, padx=10)

analyze_btn = ttk.Button(input_frame, text="Analyze", command=run_analysis)
analyze_btn.grid(row=0, column=1, padx=5)

clear_btn = ttk.Button(input_frame, text="Clear", command=clear_results)
clear_btn.grid(row=0, column=2, padx=5)

# Result Box (Scrollable)
result_frame = tk.Frame(root)
result_frame.pack(pady=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(result_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

result_text = tk.Text(result_frame, wrap="word",
                      yscrollcommand=scrollbar.set,
                      font=("Arial", 11))

result_text.pack(fill="both", expand=True)
scrollbar.config(command=result_text.yview)

# Footer
footer = tk.Label(root, text="Prototype v1 - Uses public news signals",
                  font=("Arial", 9), bg="#f4f6f8", fg="gray")
footer.pack(pady=5)

# Run app
root.mainloop()