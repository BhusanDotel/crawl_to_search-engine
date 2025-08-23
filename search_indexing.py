import json
import re
import math
from collections import defaultdict, Counter
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import tkinter as tk
from tkinter import ttk, scrolledtext
import webbrowser
import threading
from typing import List, Dict, Any

# Download required NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

class DocumentProcessor:
    """Handles text preprocessing for both documents and queries"""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text: str) -> List[str]:
        """Preprocess text: tokenize, remove stopwords, stem"""
        if not text:
            return []
            
        # Convert to lowercase and remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and short words, then stem
        processed_tokens = [
            self.stemmer.stem(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        return processed_tokens

class SearchIndex:
    """Inverted index for efficient searching"""
    
    def __init__(self):
        self.index = defaultdict(list)  # term -> [(doc_id, tf)]
        self.documents = {}  # doc_id -> document
        self.doc_frequencies = defaultdict(int)  # term -> document frequency
        self.total_docs = 0
        
    def add_documents(self, documents: List[Dict]):
        """Add documents to the index"""
        processor = DocumentProcessor()
        
        for i, doc in enumerate(documents):
            doc_id = i
            self.documents[doc_id] = doc
            
            # Combine title, abstract, and authors for indexing
            text_content = f"{doc.get('title', '')} {doc.get('abstract', '')}"
            if doc.get('authors'):
                author_names = ' '.join([author.get('name', '') for author in doc['authors']])
                text_content += f" {author_names}"
            
            # Process text and calculate term frequencies
            tokens = processor.preprocess_text(text_content)
            token_counts = Counter(tokens)
            
            # Add to inverted index
            for term, tf in token_counts.items():
                self.index[term].append((doc_id, tf))
                
            # Track which documents contain each term
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_frequencies[term] += 1
                
        self.total_docs = len(documents)
        
    def search(self, query: str, top_k: int = 20) -> List[tuple]:
        """Search for documents using TF-IDF scoring"""
        processor = DocumentProcessor()
        query_terms = processor.preprocess_text(query)
        
        if not query_terms:
            return []
            
        # Calculate document scores
        doc_scores = defaultdict(float)
        
        for term in query_terms:
            if term in self.index:
                # Calculate IDF
                df = self.doc_frequencies[term]
                idf = math.log(self.total_docs / df) if df > 0 else 0
                
                # Add TF-IDF score for each document containing this term
                for doc_id, tf in self.index[term]:
                    tf_idf = tf * idf
                    doc_scores[doc_id] += tf_idf
        
        # Sort by score (descending)
        ranked_results = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top-k results with documents
        results = []
        for doc_id, score in ranked_results[:top_k]:
            results.append((self.documents[doc_id], score))
            
        return results

class SearchEngineGUI:
    """GUI interface for the search engine"""
    
    def __init__(self, search_index: SearchIndex):
        self.search_index = search_index
        self.root = tk.Tk()
        self.root.title("Coventry University Economics Publications Search")
        self.root.geometry("1000x700")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="Coventry University - Economics, Finance & Accounting Publications",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Search frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Search:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, width=50, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<Return>', self.perform_search)
        
        search_btn = tk.Button(
            search_frame, 
            text="Search", 
            command=self.perform_search,
            font=("Arial", 12),
            bg="#4285f4",
            fg="white"
        )
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Results frame
        self.results_frame = tk.Frame(self.root)
        self.results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollable results area
        self.results_text = scrolledtext.ScrolledText(
            self.results_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for formatting
        self.results_text.tag_configure("title", font=("Arial", 12, "bold"), foreground="#1a0dab")
        self.results_text.tag_configure("authors", font=("Arial", 10), foreground="#006621")
        self.results_text.tag_configure("date", font=("Arial", 10), foreground="#808080")
        self.results_text.tag_configure("link", font=("Arial", 10, "underline"), foreground="#1a0dab")
        self.results_text.tag_configure("score", font=("Arial", 9), foreground="#808080")
        
        # Status label
        self.status_label = tk.Label(
            self.root, 
            text=f"Ready to search {self.search_index.total_docs} publications",
            font=("Arial", 10),
            fg="gray"
        )
        self.status_label.pack(pady=5)
        
    def perform_search(self, event=None):
        """Perform search and display results"""
        query = self.search_entry.get().strip()
        if not query:
            return
            
        self.status_label.config(text="Searching...")
        self.root.update()
        
        # Perform search in a separate thread to keep UI responsive
        threading.Thread(target=self._search_worker, args=(query,), daemon=True).start()
        
    def _search_worker(self, query):
        """Worker thread for performing search"""
        results = self.search_index.search(query)
        
        # Update UI in main thread
        self.root.after(0, self._display_results, query, results)
        
    def _display_results(self, query, results):
        """Display search results in the text widget"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        if not results:
            self.results_text.insert(tk.END, f"No results found for '{query}'\n\n")
            self.results_text.insert(tk.END, "Try different keywords or check spelling.")
        else:
            self.results_text.insert(tk.END, f"Found {len(results)} results for '{query}':\n\n")
            
            for i, (doc, score) in enumerate(results, 1):
                # Title (clickable link)
                title = doc.get('title', 'Untitled')
                self.results_text.insert(tk.END, f"{i}. ", "")
                
                title_start = self.results_text.index(tk.INSERT)
                self.results_text.insert(tk.END, title, "title")
                title_end = self.results_text.index(tk.INSERT)
                
                # Make title clickable
                if doc.get('link'):
                    self.results_text.tag_bind(
                        f"link_{i}", 
                        "<Button-1>", 
                        lambda e, url=doc['link']: webbrowser.open(url)
                    )
                    self.results_text.tag_add(f"link_{i}", title_start, title_end)
                
                self.results_text.insert(tk.END, "\n")
                
                # Authors
                if doc.get('authors'):
                    authors_text = "Authors: "
                    for j, author in enumerate(doc['authors']):
                        if j > 0:
                            authors_text += ", "
                        authors_text += author.get('name', 'Unknown')
                    self.results_text.insert(tk.END, authors_text + "\n", "authors")
                
                # Publication date
                if doc.get('publishedDate'):
                    self.results_text.insert(tk.END, f"Published: {doc['publishedDate']}\n", "date")
                
                # Abstract (truncated)
                if doc.get('abstract'):
                    abstract = doc['abstract'][:300] + "..." if len(doc['abstract']) > 300 else doc['abstract']
                    self.results_text.insert(tk.END, f"{abstract}\n")
                
                # Links
                if doc.get('link'):
                    link_text = f"📄 View Publication"
                    link_start = self.results_text.index(tk.INSERT)
                    self.results_text.insert(tk.END, link_text, "link")
                    link_end = self.results_text.index(tk.INSERT)
                    
                    # Make link clickable
                    self.results_text.tag_bind(
                        f"pub_link_{i}", 
                        "<Button-1>", 
                        lambda e, url=doc['link']: webbrowser.open(url)
                    )
                    self.results_text.tag_add(f"pub_link_{i}", link_start, link_end)
                
                # Relevance score (for debugging)
                self.results_text.insert(tk.END, f" (Relevance: {score:.2f})", "score")
                self.results_text.insert(tk.END, "\n" + "─"*80 + "\n\n")
        
        self.results_text.config(state=tk.DISABLED)
        self.status_label.config(text=f"Search completed. Found {len(results)} results.")
        
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def load_data(filename: str) -> List[Dict]:
    """Load scraped data from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        print("Please make sure your scraped data is saved as 'publications.json'")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{filename}'")
        return []

def main():
    """Main function to run the search engine"""
    print("Loading publications data...")
    
    # Load your scraped data (update filename as needed)
    publications = load_data('publications.json')
    
    if not publications:
        print("No data loaded. Please check your data file.")
        return
    
    print(f"Loaded {len(publications)} publications")
    print("Building search index...")
    
    # Create search index
    search_index = SearchIndex()
    search_index.add_documents(publications)
    
    print("Search index built successfully!")
    print("Starting search interface...")
    
    # Launch GUI
    app = SearchEngineGUI(search_index)
    app.run()

if __name__ == "__main__":
    main()