import json
import pandas as pd
from jobspy import scrape_jobs
import time

def test_scrape():
    company = "Salesforce"
    keyword = "salesforce"
    search_term = f"{keyword} {company}"
    location = "India"
    
    print(f"Scraping for {company}")
    jobs = scrape_jobs(
        site_name=["linkedin", "google"],
        search_term=search_term,
        location=location,
        results_wanted=10,
        country_indeed='india'
    )
    print(f"Total jobs returned: {len(jobs)}")
    if not jobs.empty:
        print("\nCompany names found:")
        print(jobs['company'].unique())
        
        filtered = jobs[jobs['company'].str.lower().str.contains(company.lower(), na=False)]
        print(f"\nJobs after filter: {len(filtered)}")
        
if __name__ == '__main__':
    test_scrape()
