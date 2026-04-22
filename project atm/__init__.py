import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import spacy
import urllib.parse

# Load Spacy's light English model for location extraction
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os

    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


class ViewTripAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("ViewTrip | Travel Propensity Scorer")
        self.root.geometry("600x550")
        self.root.configure(bg="#f4f7f6")

        # --- UI Header ---
        header_frame = tk.Frame(root, bg="#1a2a6c", height=80)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="ANALYTICS", font=("Helvetica", 16, "bold"),
                 bg="#1a2a6c", fg="white").pack(pady=20)

        # --- Inputs ---
        main_frame = tk.Frame(root, bg="#f4f7f6")
        main_frame.pack(pady=20, padx=40, fill="both")

        tk.Label(main_frame, text="Company Name:", bg="#f4f7f6", font=("Arial", 10, "bold")).pack(anchor="w")
        self.company_entry = tk.Entry(main_frame, font=("Arial", 12), width=40)
        self.company_entry.pack(pady=5, fill="x")

        tk.Label(main_frame, text="Expected HQ City (e.g. Lagos):", bg="#f4f7f6", font=("Arial", 10)).pack(anchor="w")
        self.hq_entry = tk.Entry(main_frame, font=("Arial", 12), width=40)
        self.hq_entry.insert(0, "Lagos")
        self.hq_entry.pack(pady=5, fill="x")

        self.run_btn = tk.Button(main_frame, text="SCAN PUBLIC DATA", command=self.process_analysis,
                                 bg="#b21f1f", fg="white", font=("Arial", 11, "bold"), height=2)
        self.run_btn.pack(pady=20, fill="x")

        # --- Output ---
        self.result_frame = tk.LabelFrame(main_frame, text="Live Insights", bg="white", padx=15, pady=15)
        self.result_frame.pack(fill="both", expand=True)


        self.score_label = tk.Label(self.result_frame, text="Score: --%", font=("Impact", 24), bg="white", fg="#7f8c8d")
        self.score_label.pack()

        self.loc_list = tk.Text(self.result_frame, height=6, font=("Consolas", 9), state="disabled", bg="#f9f9f9")
        self.loc_list.pack(pady=10, fill="x")
        self.run_btn = tk.Button(main_frame, text="SCAN PUBLIC DATA", command=self.process_analysis,
                                 bg="#b21f1f", fg="white", font=("Arial", 11, "bold"), height=2)
        self.run_btn.pack(pady=20, fill="x")

    def fetch_google_data(self, query):
        """Perform a basic search. Note: Frequent use might trigger a CAPTCHA."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract snippets from Google search results
            snippets = [div.get_text() for div in soup.find_all('div', class_='VwiC3b')]
            return " ".join(snippets)
        except Exception as e:
            return ""

    def process_analysis(self):
        company = self.company_entry.get().strip()
        hq_city = self.hq_entry.get().strip()

        if not company:
            messagebox.showerror("Error", "Please enter a company name.")
            return

        self.run_btn.config(text="SCANNING...", state="disabled")
        self.root.update()

        # Step 1: Search for project history
        search_query = f"{company} recent projects and locations"
        raw_text = self.fetch_google_data(search_query)

        if not raw_text:
            messagebox.showwarning("No Data", "Could not retrieve public data. Check your connection.")
            self.run_btn.config(text="SCAN PUBLIC DATA", state="normal")
            return

        # Step 2: Use NLP to extract locations
        doc = nlp(raw_text)
        found_locations = set()
        for ent in doc.ents:
            if ent.label_ == "GPE":  # GPE = Countries, Cities, States
                found_locations.add(ent.text)

        # Step 3: Calculate travel probability
        # Logic: If locations found are NOT the HQ city, travel is likely.
        remote_locations = [loc for loc in found_locations if hq_city.lower() not in loc.lower()]

        # Simple scoring logic
        if not found_locations:
            score = 0
        else:
            # More remote locations = higher score
            score = min(100, (len(remote_locations) / (len(found_locations) + 1)) * 150)

        # Update UI
        color = "#e74c3c" if score > 60 else "#27ae60"
        self.score_label.config(text=f"Travel Score: {score:.1f}%", fg=color)

        self.loc_list.config(state="normal")
        self.loc_list.delete(1.0, tk.END)
        self.loc_list.insert(tk.END,
                             f"Analyzed Projects in: {', '.join(remote_locations) if remote_locations else 'No remote sites found.'}")
        self.loc_list.config(state="disabled")

        self.run_btn.config(text="SCAN PUBLIC DATA", state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = ViewTripAnalyzer(root)
    root.mainloop()