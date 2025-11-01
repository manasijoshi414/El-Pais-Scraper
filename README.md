Hi, Welcome to El Pais website scraper.

## This project will:
   1. Scrape the first 5 articles from El País Opinion section.
   2. Display content in Spanish.
   3. Download cover images for each article.
   4. Translate article titles to English using Rapid Translate API.
   5. Analyze repeated words in translated titles.
   6. Cross-browser testing with BrowserStack.


## Steps to set it up and run (Make sure to have python installed before following these steps):

   1. Install dependencies via your terminal/bash: 
         pip3 install --user -r requirements.txt

   2. Get RapidAPI key:
      - Sign up at RapidAPI- https://rapidapi.com/
      - Subscribe to Rapid Translate Multi Traduction API - https://rapidapi.com/sibaridev/api/rapid-translate-multi-traduction
      - Update your API key in `elpais_scraper.py`:

   3. Create images directory:
         mkdir -p images

   4. Run the script:
         python elpais_scraper.py

   5. BrowserStack testing:
      - Create a free trial account at BrowserStack- https://www.browserstack.com/
      - Update credentials in `browserstack_test.py`

   6. Run cross-browser tests:
         python3 browserstack_test.py


## Files

- `elpais_scraper.py` - Main scraping script
- `browserstack_test.py` - Cross-browser testing script
- `requirements.txt` - Python dependencies
- `setup.sh` - Setup script
- `images/` - Downloaded article images
- `README.md` - This file


## Notes

- The scraper includes rate limiting to be respectful to the website
- Images are saved as JPG files in the `images/` directory
- Translation uses Rapid Translate Multi Traduction API
- BrowserStack requires account setup for cross-browser testing