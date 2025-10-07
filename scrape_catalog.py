import requests
from bs4 import BeautifulSoup
import json
import re

# Configuration
CATALOG_INDEX_URL = 'https://catalog.ucsd.edu/front/courses.html'
BASE_URL = 'https://catalog.ucsd.edu/'
OUTPUT_FILE = 'course_data.json'
REQUEST_TIMEOUT = 15 

def get_department_links(index_url):
    # (This function is proven to work and remains the same)
    print(f"1. Fetching department index from: {index_url}")
    try:
        response = requests.get(index_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching index page: {e}")
        return {}

    soup = BeautifulSoup(response.content, 'html.parser')
    department_links = {}

    for link in soup.select('a'):
        href = link.get('href')
        text = link.text.strip()
        
        if href and 'courses/' in href and href.endswith('.html') and text:
            dept_code_match = re.search(r'courses/([A-Z]+)\.html', href)
            
            if dept_code_match:
                dept_code = dept_code_match.group(1)
                full_url = requests.compat.urljoin(BASE_URL, href)
                if len(dept_code) >= 2 and len(dept_code) <= 5: 
                    department_links[dept_code] = full_url

    print(f"   -> Found {len(department_links)} department pages.")
    return department_links

def scrape_department_page(dept_code, url):
    """
    Visits a single department page and extracts all course details.
    FIX: Targets the specific 'course-name' CSS class in <p> tags.
    """
    course_list = []
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"   Error fetching {dept_code} page: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    course_title_elements = soup.find_all('p', class_='course-name')

    if not course_title_elements:
         print(f"      -> Warning: No elements with class 'course-name' found for {dept_code}. Structure changed.")
         return []

    for title_element in course_title_elements:
        title_text = title_element.text.strip()
        
        # Ensure the element actually contains a course listing
        if not title_text.startswith(dept_code):
            continue 
            
        # --- ROBUST REGEX (The most successful pattern from before) ---
        # Pattern: DEPT NUMBER. TITLE (CREDITS) - Group 1: Number, Group 2: Title, Group 3: Credits
        pattern_strict = r'^\s*' + re.escape(dept_code) + r'\s*(\d+[A-Z]*)\.\s*(.*?)\s*\((\d+)\)\s*$'
        
        match = re.search(pattern_strict, title_text, re.IGNORECASE)
        credits = 4 # Default credits

        if match:
            course_number = match.group(1).upper()
            course_title = match.group(2).strip()
            credits = int(match.group(3))
        else:
             # Fallback logic to still capture the number and title if credits or period are missing
             pattern_loose = r'^\s*' + re.escape(dept_code) + r'\s*(\d+[A-Z]*)\s*\.?\s*(.*?)$'
             match_loose = re.search(pattern_loose, title_text, re.IGNORECASE)
             if not match_loose:
                 continue
             
             course_number = match_loose.group(1).upper()
             course_title = match_loose.group(2).strip()

        # Find description: The description is typically in the next <p> sibling 
        # that *does not* have the 'course-name' class.
        description_element = title_element.find_next_sibling('p')
        
        # Validate the sibling is not another course title
        if description_element and 'course-name' not in description_element.get('class', []):
            description = description_element.text.strip()
        else:
            description = "No description found."
        
        # Final sanity check before appending
        if course_number.isdigit() or re.search(r'\d', course_number):
            course_list.append({
                "department": dept_code,
                "course_number": course_number,
                "title": course_title,
                "description": description,
                "credits": credits
            })
            
    return course_list

def main():
    """
    Main function to run the scraping process and save data to JSON.
    """
    all_courses = []
    dept_links = get_department_links(CATALOG_INDEX_URL)
    
    print("-" * 50)
    print(f"2. Extracting courses from {len(dept_links)} departments...")

    for dept_code, url in dept_links.items():
        courses = scrape_department_page(dept_code, url)
        all_courses.extend(courses)
        print(f"      -> Extracted {len(courses)} courses for {dept_code}.")
    
    print("-" * 50)
    print(f"3. Total courses extracted: {len(all_courses)}")

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_courses, f, indent=2)
        
    print(f"4. Successfully saved course data to {OUTPUT_FILE}")

if __name__ == '__main__':
    main()