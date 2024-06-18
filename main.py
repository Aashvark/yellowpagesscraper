import time, google_sheets_access
import selenium
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome(options=options)
includedTypes = ["real estate agent", "real estate agency", "insurance_agency", "lawyer", "car_dealer", "car_rental", "car_repair", "car_wash", "art_gallery", "museum", "performing_arts_theater", "library", "amusement_center", "amusement_park", "aquarium", "banquet_hall", "bowling_alley", "casino", "event_venue", "night_club", "wedding_venue", "accounting", "dental_clinic", "dentist", "doctor", "hospital", "physiotherapist", "spa", "extended_stay_hotel", "hotel", "resort_hotel", "beauty_salon", "child_care_agency", "consultant", "electrician", "florist", "funeral_home", "hair_care", "hair_salon", "locksmith", "moving_company", "plumber", "roofing_contractor", "veterinary_care", "auto_parts_store", "electronics_store", "home_improvement_store", "jewelry_store", "fitness_center", "gym", "ski_resort", "sports_club", "sports_complex"]
addressl = "10863 West Bloomingdale Avenue, Riverview, FL  33578" # Address
sheet = "TAM2002-D01" # Google Sheets Sheets Name
locations = []

for term in includedTypes:
    link = f"https://www.yellowpages.com/search?search_terms={term.replace("_", "+")}&geo_location_terms={quote(addressl)}"
    driver.get(link)
    try:
        records = driver.find_element(By.ID, "main-content").find_element(By.CLASS_NAME, "scrollable-pane").find_element(By.CLASS_NAME, "organic").find_elements(By.CLASS_NAME, "result")
    except:
        continue
    
    for record in records:
        info = record.find_element(By.CLASS_NAME, "srp-listing").find_element(By.CLASS_NAME, "v-card").find_element(By.CLASS_NAME, "info")
        name = info.find_element(By.CLASS_NAME, "info-primary").find_element(By.CSS_SELECTOR, "h2.n").find_element(By.CLASS_NAME, "business-name").find_element(By.CSS_SELECTOR, "span").get_property("textContent")

        if True in [n.lower() in name.lower() for n in ["Aflac", "Allstate", "Progressive", "Mayo Clinic", "Hampton", "Marriott", "Margaritaville", "Spectrum", "Supercuts", "Sport Clips", "Banfield", "AutoZone", "Mavis Tires", "O'Reilly", "Verizon", "Metro Pcs", "RadioShack", "Best Buy", "Apple Store", "Circle K", "Speedway", "Bealls", "7-Eleven", "Walmart", "Dollar Tree", "Sears", "Target", "Walgreens", "Mobil", "Publix", "WaWa", "Dollar Express", "Big Lots", "SEPHORA", "Kohl's", "Kohls", "Orangetheory", "Mayo Clinic", "Planet Fitness"]]:
            continue
        
        try:
            website = info.find_element(By.CLASS_NAME, "info-primary").find_element(By.CLASS_NAME, "links").find_element(By.CSS_SELECTOR, "a.track-visit-website").get_property("href")
        except selenium.common.exceptions.NoSuchElementException:
            website = " "

        try:
            phone = info.find_element(By.CLASS_NAME, "info-secondary").find_element(By.CLASS_NAME, "phone").get_property("textContent")
        except:
            phone = " "

        try:
            adr = info.find_element(By.CLASS_NAME, "info-secondary").find_element(By.CLASS_NAME, "adr")
            try:
                address = adr.find_element(By.CLASS_NAME, "street-address").get_property("textContent")
            except selenium.common.exceptions.NoSuchElementException:
                address = " "
            
            try:
                locality = adr.find_element(By.CLASS_NAME, "locality").get_property("textContent")
            except selenium.common.exceptions.NoSuchElementException:
                locality = " "
        except:
            address = " "
            locality = " "

        full = address + " " + locality

        if ([name, term, full, " ", phone, website] not in locations):
            locations.append([name, term, full, " ", phone, website])

driver.close()

with open("fail_safe.csv", "w+") as f:
    f.write("\n".join([",".join(l) for l in locations]))
    f.close()

gsm = google_sheets_access.GoogleManager()
id = "" # Google Sheets Webpage ID https://docs.google.com/spreadsheets/d/[HERE]/edit, do not leave it blank 

gsm.update(
    id,
    f"{sheet}!A2:F{1 + len(locations)}",
    "USER_ENTERED",
    locations
)
