


#!/usr/bin/env python3
"""
Professional Web Scraper with Automation Utils
Scrapes quotes from quotes.toscrape.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import logging
import sys
import os
import shutil  # ✅ MOVED TO TOP

# FIX THE PATH - Go up TWO levels to find automation_utils.py
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, ROOT_DIR)

# Now import will work!
from automation_utils import (
    setup_logging,
    create_output_directory,
    save_to_csv,
    remove_duplicates
)

# Import config from current directory
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

from config import (
    CLIENT_NAME,
    PROJECT_NAME,
    BASE_URL,
    NUM_PAGES,
    OUTPUT_FILE,
    LOG_FILE, 
    HEADERS
)


def scrape_single_page(url):
    """
    Scrape quotes from a single page
    
    Args:
        url (str): URL to scrape
        
    Returns:
        list: List of dictionaries with quote and author
    """
    try:
        print(f"📄 Scraping: {url}")
        response.raise_for_status()
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all quotes and authors
        quotes = soup.find_all('span', class_='text')
        authors = soup.find_all('small', class_='author')
        
        # Build data list
        data = []
        for quote, author in zip(quotes, authors):
            data.append({
                'quote': quote.text,
                'author': author.text
            })
        
        print(f"   ✅ Found {len(data)} quotes")
        logging.info(f"Scraped {len(data)} quotes from {url}")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network Error: {e}")
        logging.error(f"Network error on {url}: {e}")
        return []
    except Exception as e:
        print(f"   ❌ Error: {e}")
        logging.error(f"Error scraping {url}: {e}")
        return []


def generate_statistics(df):
    """Generate and print statistics about the data"""
    print(f"\n📊 STATISTICS:")
    print(f"   Total quotes: {len(df)}")
    print(f"   Unique authors: {df['author'].nunique()}")
    
    print(f"\n   Top 5 Most Quoted Authors:")
    for author, count in df['author'].value_counts().head(5).items():
        print(f"      {count}x - {author}")
    
    # Log statistics
    logging.info(f"Statistics - Total: {len(df)}, Unique authors: {df['author'].nunique()}")


def generate_report(df, dup_count, output_dir, output_path):
    """Generate detailed text report"""
    report = f"""
{'='*60}
WEB SCRAPING REPORT
{'='*60}

Project: {PROJECT_NAME}
Client: {CLIENT_NAME}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SCRAPING DETAILS:
- Base URL: {BASE_URL}
- Pages scraped: {NUM_PAGES}
- Total quotes collected: {len(df)}
- Unique authors: {df['author'].nunique()}
- Duplicates removed: {dup_count}

TOP 5 AUTHORS:
{df['author'].value_counts().head(5).to_string()}

ALL UNIQUE AUTHORS ({df['author'].nunique()}):
{', '.join(sorted(df['author'].unique()))}

OUTPUT FILES:
- Data: {output_path}
- Report: {os.path.join(output_dir, 'report.txt')}
- Log: {os.path.join(output_dir, 'logs', LOG_FILE)}

{'='*60}
"""
    
    report_path = os.path.join(output_dir, 'report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Report saved: {report_path}")
    logging.info(f"Report generated: {report_path}")
    
    return report_path


def main():
    """Main execution function"""
    print("="*60)
    print(f"🕷️  {PROJECT_NAME}")
    print(f"👤 Client: {CLIENT_NAME}")
    print("="*60)
    
    # Setup logging FIRST
    setup_logging(LOG_FILE)
    logging.info("="*60)
    logging.info(f"Starting scraping: {PROJECT_NAME}")
    logging.info("="*60)
    
    # SCRAPE MULTIPLE PAGES
    all_quotes = []
    
    print(f"\n🔄 Scraping {NUM_PAGES} pages...\n")
    
    for page_num in range(1, NUM_PAGES + 1):
        url = f"{BASE_URL}/page/{page_num}/"
        page_data = scrape_single_page(url)
        all_quotes.extend(page_data)
        
        # Polite delay between requests
        if page_num < NUM_PAGES:
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"🎯 Total quotes collected: {len(all_quotes)}")
    print(f"{'='*60}")
    
    # CREATE DATAFRAME
    if not all_quotes:
        print("❌ No data collected! Exiting.")
        logging.error("No data collected")
        return
    
    df = pd.DataFrame(all_quotes)
    
    # CLEAN DATA
    initial_count = len(df)
    df, dup_count = remove_duplicates(df)
    
    if dup_count > 0:
        print(f"\n🧹 Data Cleaning:")
        print(f"   Initial records: {initial_count}")
        print(f"   Duplicates removed: {dup_count}")
        print(f"   Final records: {len(df)}")
        logging.info(f"Removed {dup_count} duplicates")
    
    # GENERATE STATISTICS
    generate_statistics(df)
    
    # CREATE OUTPUT DIRECTORY (MUST BE BEFORE MOVING LOG!)
    output_dir = create_output_directory(CLIENT_NAME)
    print(f"\n📁 Output directory: {output_dir}")
    
    # SAVE CSV
    output_path = os.path.join(output_dir, OUTPUT_FILE)
    save_to_csv(df, output_path)
    print(f"💾 Data saved: {output_path}")
    
    # MOVE LOG FILE TO OUTPUT DIRECTORY (SAFE METHOD)
    if os.path.exists(LOG_FILE):
        try:
            # Create logs subdirectory
            logs_dir = os.path.join(output_dir, 'logs')
            os.makedirs(logs_dir, exist_ok=True)
            
            # Move log file
            log_destination = os.path.join(logs_dir, os.path.basename(LOG_FILE))
            shutil.move(LOG_FILE, log_destination)
            print(f"📋 Log saved: {log_destination}")
        except Exception as e:
            print(f"⚠️  Could not move log file: {e}")
            logging.warning(f"Could not move log file: {e}")
    else:
        print(f"⚠️  Log file not found: {LOG_FILE}")
    
    # GENERATE REPORT
    generate_report(df, dup_count, output_dir, output_path)
    
    # FINAL SUMMARY
    print(f"\n{'='*60}")
    print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    print(f"\n📦 All files saved in: {output_dir}")
    print(f"\n🎉 Done! Check the output folder for:")
    print(f"   1. {OUTPUT_FILE} - Your data")
    print(f"   2. report.txt - Detailed report")
    print(f"   3. logs/{LOG_FILE} - Execution log")
    print(f"\n{'='*60}\n")
    
    # Debug info (optional - can remove in production)
    print(f"🔍 Debug Info:")
    print(f"   ROOT_DIR: {ROOT_DIR}")
    print(f"   Files in ROOT: {', '.join(os.listdir(ROOT_DIR)[:5])}...")
    
    logging.info("Scraping completed successfully")
    logging.info("="*60)


if __name__ == "__main__":
    main()



