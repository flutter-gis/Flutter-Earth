import sys
import os
import threading
import json
import time
import requests
from queue import Queue
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext

class SimpleCrawlerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Earth Engine Catalog Web Crawler - Simple")
        self.root.geometry("900x600")
        
        self.log_queue = Queue()
        self.progress_queue = Queue()
        self.thread = None
        self.output_dir = "extracted_data"
        self.images_dir = "thumbnails"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.images_dir, exist_ok=True)
        
        self.setup_ui()
        self.update_ui()

    def setup_ui(self):
        # File selection frame
        file_frame = ttk.LabelFrame(self.root, text="HTML File Selection", padding="10")
        file_frame.pack(fill="x", padx=10, pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_file)
        self.browse_btn.pack(side="right")
        
        # Options frame
        options_frame = ttk.LabelFrame(self.root, text="Crawling Options", padding="10")
        options_frame.pack(fill="x", padx=10, pady=5)
        
        self.download_thumbs_var = tk.BooleanVar(value=True)
        self.extract_details_var = tk.BooleanVar(value=True)
        self.save_individual_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Download thumbnails", variable=self.download_thumbs_var).pack(anchor="w")
        ttk.Checkbutton(options_frame, text="Extract detailed information", variable=self.extract_details_var).pack(anchor="w")
        ttk.Checkbutton(options_frame, text="Save as individual JSON files", variable=self.save_individual_var).pack(anchor="w")
        
        # Status and progress
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_var = tk.StringVar(value="Ready. Select an HTML file to begin.")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.pack(anchor="w")
        
        self.progress = ttk.Progressbar(status_frame, mode='determinate', maximum=100)
        self.progress.pack(fill="x", pady=(5, 0))
        
        # Console output
        console_frame = ttk.LabelFrame(self.root, text="Console Output", padding="10")
        console_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame, height=15, bg='black', fg='white', font=('Consolas', 10))
        self.console.pack(fill="both", expand=True)
        
        # Control buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.crawl_btn = ttk.Button(button_frame, text="Start Crawling", command=self.start_crawl, state="disabled")
        self.crawl_btn.pack(side="left", padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", command=self.stop_crawl, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Console", command=self.clear_console)
        self.clear_btn.pack(side="left")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select HTML File",
            filetypes=[("HTML Files", "*.html *.htm"), ("All Files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.crawl_btn.config(state="normal")
            self.log_message(f"Selected file: {file_path}")

    def log_message(self, message):
        self.log_queue.put(f"[{time.strftime('%H:%M:%S')}] {message}")

    def clear_console(self):
        self.console.delete(1.0, tk.END)

    def start_crawl(self):
        html_file = self.file_path_var.get()
        if not html_file or not os.path.exists(html_file):
            self.log_message("ERROR: Please select a valid HTML file")
            return
        
        self.console.delete(1.0, tk.END)
        self.status_var.set("Crawling...")
        self.progress['value'] = 0
        self.crawl_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.browse_btn.config(state="disabled")
        
        self.thread = threading.Thread(
            target=self.crawl_html_file, 
            args=(html_file, self.log_queue, self.progress_queue),
            daemon=True
        )
        self.thread.start()

    def stop_crawl(self):
        if self.thread and self.thread.is_alive():
            self.log_message("Stopping crawler...")
            self.stop_requested = True

    def update_ui(self):
        # Process log messages
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.console.insert(tk.END, msg + "\n")
            self.console.see(tk.END)
            if "[DONE]" in msg or "[ERROR]" in msg:
                self.status_var.set("Done!")
                self.crawl_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.browse_btn.config(state="normal")
        
        # Process progress updates
        while not self.progress_queue.empty():
            val = self.progress_queue.get()
            self.progress['value'] = val
        
        # Check if thread is still alive
        if self.thread and not self.thread.is_alive():
            self.crawl_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.browse_btn.config(state="normal")
        
        # Schedule next update
        self.root.after(100, self.update_ui)

    def crawl_html_file(self, html_file, log_queue, progress_queue):
        try:
            log_queue.put(f"Starting crawl of: {html_file}")
            
            # Read the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            log_queue.put("Parsing HTML content...")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all dataset links
            links = soup.find_all('a', href=True)
            dataset_links = []
            
            for link in links:
                href = link.get('href')
                if href and ('catalog' in href or 'datasets' in href):
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = f"https://developers.google.com{href}"
                    elif not href.startswith('http'):
                        href = urljoin("https://developers.google.com/earth-engine/datasets/", href)
                    dataset_links.append(href)
            
            log_queue.put(f"Found {len(dataset_links)} potential dataset links")
            
            # Remove duplicates
            dataset_links = list(set(dataset_links))
            log_queue.put(f"Unique links to process: {len(dataset_links)}")
            
            # Setup webdriver for detailed crawling
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            driver = webdriver.Edge(options=options)
            
            processed_count = 0
            total_links = len(dataset_links)
            
            for i, link in enumerate(dataset_links):
                if hasattr(self, 'stop_requested') and self.stop_requested:
                    log_queue.put("Crawling stopped by user")
                    break
                
                try:
                    log_queue.put(f"Processing {i+1}/{total_links}: {link}")
                    
                    # Get the page content
                    driver.get(link)
                    time.sleep(2)  # Wait for page to load
                    
                    page_html = driver.page_source
                    page_soup = BeautifulSoup(page_html, 'html.parser')
                    
                    # Extract dataset information
                    dataset_data = self.extract_dataset_info(page_soup, link)
                    
                    if dataset_data:
                        # Download thumbnail if requested
                        if self.download_thumbs_var.get() and dataset_data.get('thumbnail_url'):
                            thumb_path = self.download_image(dataset_data['thumbnail_url'])
                            dataset_data['thumbnail_path'] = thumb_path
                        
                        # Save as individual JSON file
                        if self.save_individual_var.get():
                            safe_title = "".join(c for c in dataset_data.get('title', 'dataset') if c.isalnum() or c in (' ', '-', '_')).rstrip()
                            safe_title = safe_title[:50]  # Limit length
                            json_filename = f"{safe_title}_{i}.json"
                            json_path = os.path.join(self.output_dir, json_filename)
                            
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(dataset_data, f, ensure_ascii=False, indent=2)
                            
                            log_queue.put(f"Saved: {json_filename}")
                            processed_count += 1
                    
                    # Update progress
                    progress = int((i + 1) / total_links * 100)
                    progress_queue.put(progress)
                    
                    # Small delay to be respectful
                    time.sleep(0.5)
                    
                except Exception as e:
                    log_queue.put(f"ERROR processing {link}: {str(e)}")
                    continue
            
            driver.quit()
            
            log_queue.put(f"[DONE] Crawling complete! Processed {processed_count} datasets.")
            log_queue.put(f"Data saved to: {self.output_dir}")
            if self.download_thumbs_var.get():
                log_queue.put(f"Thumbnails saved to: {self.images_dir}")
            
        except Exception as e:
            log_queue.put(f"[ERROR] Crawling failed: {str(e)}")

    def extract_dataset_info(self, soup, url):
        """Extract dataset information from a page"""
        data = {
            'url': url,
            'title': None,
            'description': None,
            'thumbnail_url': None,
            'metadata': {},
            'tags': [],
            'provider': None
        }
        
        # Extract title
        title_elem = soup.find('h1') or soup.find('title')
        if title_elem:
            data['title'] = title_elem.get_text(strip=True)
        
        # Extract description
        desc_elem = soup.find('div', class_='devsite-article-body') or soup.find('p')
        if desc_elem:
            data['description'] = desc_elem.get_text(strip=True)
        
        # Extract thumbnail
        img_elem = soup.find('img')
        if img_elem and img_elem.get('src'):
            src = img_elem['src']
            if not src.startswith('http'):
                src = urljoin(url, src)
            data['thumbnail_url'] = src
        
        # Extract metadata from tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    if key and value:
                        data['metadata'][key] = value
        
        # Extract tags/chips
        chips = soup.find_all('span', class_='devsite-chip-label')
        data['tags'] = [chip.get_text(strip=True) for chip in chips if chip.get_text(strip=True)]
        
        # Extract provider
        provider_elem = soup.find('a', class_='devsite-link')
        if provider_elem:
            data['provider'] = provider_elem.get_text(strip=True)
        
        return data

    def download_image(self, url):
        """Download an image and return the local path"""
        if not url:
            return None
        
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                filename = f"thumb_{int(time.time())}.jpg"
            
            filepath = os.path.join(self.images_dir, filename)
            
            headers = {"User-Agent": "Mozilla/5.0 (compatible; EarthEngineCrawler/1.0)"}
            response = requests.get(url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            
            return filepath
            
        except Exception as e:
            self.log_queue.put(f"Failed to download image {url}: {str(e)}")
            return None

def main():
    root = tk.Tk()
    app = SimpleCrawlerUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 