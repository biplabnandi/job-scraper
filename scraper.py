import json
import pandas as pd
from jobspy import scrape_jobs
from datetime import datetime
import os
import time
import random

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    config = load_config()
    keyword = config.get("keyword", "")
    companies = config.get("companies", [])
    location = config.get("location", "India")
    is_remote = config.get("is_remote", True)
    results_per_company = config.get("results_per_company", 20)
    
    all_jobs = []

    for company in companies:
        print(f"Scraping jobs for {company}...")
        search_term = f"{keyword} {company}"
        
        try:
            jobs = scrape_jobs(
                site_name=["linkedin", "google"],
                search_term=search_term,
                location=location,
                results_wanted=results_per_company,
                is_remote=is_remote,
                country_indeed='india'
            )
            
            if not jobs.empty:
                # Filter results to make sure the company name matches reasonably well
                filtered_jobs = jobs[jobs['company'].str.lower().str.contains(company.lower(), na=False)]
                all_jobs.append(filtered_jobs)
                print(f"Found {len(filtered_jobs)} matching jobs for {company}.")
            else:
                print(f"No jobs found for {company}.")
                
        except Exception as e:
            print(f"Error scraping for {company}: {e}")
            
        # Add a random delay to prevent rate-limiting/blocking from job boards
        delay = random.uniform(2.5, 5.0)
        print(f"Sleeping for {delay:.1f} seconds to avoid rate limits...")
        time.sleep(delay)

    if not all_jobs:
        print("No jobs found across all companies.")
        with open("jobs_report.md", "w", encoding="utf-8") as f:
            f.write("# Job Scraper Report\n\nNo jobs found at this time.\n")
        return

    # Combine all results
    final_df = pd.concat(all_jobs, ignore_index=True)
    
    # Drop duplicates based on job title and company
    final_df = final_df.drop_duplicates(subset=['title', 'company', 'location'])
    
    # Ensure 'date_posted' is datetime for sorting
    if 'date_posted' in final_df.columns:
        final_df['date_posted'] = pd.to_datetime(final_df['date_posted'], errors='coerce')
    else:
        final_df['date_posted'] = pd.NaT

    # Prepare markdown
    md_lines = []
    md_lines.append(f"# Job Scraper Report")
    md_lines.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    # Group by company and location
    grouped = final_df.groupby(['company', 'location'], dropna=False)
    
    for (company, loc), group in grouped:
        md_lines.append(f"## {company} - {loc if pd.notna(loc) else 'Location Not Specified'}")
        md_lines.append("| Date | Job Title | Link |")
        md_lines.append("|---|---|---|")
        
        # Sort each group by date_posted descending
        group_sorted = group.sort_values(by='date_posted', ascending=False)
        
        for _, row in group_sorted.iterrows():
            date_str = row['date_posted'].strftime('%Y-%m-%d') if pd.notna(row['date_posted']) else 'Unknown'
            title = str(row.get('title', 'Unknown')).replace('|', '\\|')
            link = row.get('job_url', '#')
            md_lines.append(f"| {date_str} | {title} | [Apply]({link}) |")
            
        md_lines.append("") # Empty line between groups

    with open("jobs_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
        
    print("Report generated successfully as jobs_report.md")

if __name__ == "__main__":
    main()
