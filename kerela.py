# import csv
# import time
# import logging
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
# from webdriver_manager.chrome import ChromeDriverManager

# # Setup logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[logging.FileHandler("rera_scraper.log"), logging.StreamHandler()]
# )
# logger = logging.getLogger(__name__)

# def setup_driver():
#     chrome_options = Options()
#     chrome_options.add_argument("--window-size=1920,1080")
#     chrome_options.add_argument("--disable-notifications")
#     chrome_options.add_argument("--disable-popup-blocking")
#     # Uncomment the line below if you want to run headless
#     # chrome_options.add_argument("--headless")
#     return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# def wait_for_element(driver, xpath, timeout=20):
#     try:
#         return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
#     except TimeoutException:
#         logger.error(f"Timeout waiting for element: {xpath}")
#         return None

# def handle_popups(driver):
#     try:
#         buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'close')] | //div[contains(@class, 'popup')]//button | //div[contains(@class, 'modal')]//button")
#         for button in buttons:
#             if button.is_displayed():
#                 button.click()
#                 time.sleep(1)
#     except Exception as e:
#         logger.warning(f"Popup handling error: {e}")

# def switch_to_new_tab(driver):
#     try:
#         WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
#         driver.switch_to.window(driver.window_handles[-1])
#         WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
#         time.sleep(5)
#         return True
#     except Exception as e:
#         logger.error(f"Error switching tab: {e}")
#         return False

# def click_construction_progress_tab(driver):
#     try:
#         # Try multiple possible ways to find and click the Construction Progress tab
#         for xpath in [
#             "//a[@href='#tab4']", 
#             "//a[contains(text(), 'Construction Progress')]",
#             "//ul[contains(@class, 'nav-tabs')]//a[contains(text(), 'Construction')]",
#             "//div[contains(@class, 'nav')]//a[contains(text(), 'Construction')]",
#             "//li/a[contains(text(), 'Building Progress')]"
#         ]:
#             tab = wait_for_element(driver, xpath, timeout=5)
#             if tab:
#                 driver.execute_script("arguments[0].scrollIntoView(true);", tab)
#                 time.sleep(1)
#                 driver.execute_script("arguments[0].click();", tab)
#                 time.sleep(3)
#                 return True
#     except Exception as e:
#         logger.error(f"Click tab error: {e}")
#     return False

# def extract_building_details(driver):
#     """Extract ONLY the main building details table from the page"""
#     try:
#         # Look specifically for the main building details table
#         building_data = []
#         building_headers = []
        
#         # Try various XPaths to find the Building Details table
#         for xpath in [
#             "//div[contains(text(), 'Building Details')]/following::table[1]",
#             "//h4[contains(text(), 'Building Details')]/following::table[1]",
#             "//div[@id='tab4']//table[1]",  # Often the first table is the building details
#             "//table[.//th[contains(text(), 'Building Name')]]"
#         ]:
#             table = driver.find_elements(By.XPATH, xpath)
#             if table:
#                 table = table[0]  # Get the first matching table
                
#                 # Get the headers
#                 header_cells = table.find_elements(By.TAG_NAME, "th")
#                 if not header_cells:
#                     continue
                    
#                 headers = [cell.text.strip() for cell in header_cells]
                
#                 # Verify this is the building details table
#                 if not any("Building Name" in header for header in headers):
#                     continue
                    
#                 # Get data rows
#                 rows = table.find_elements(By.TAG_NAME, "tr")
#                 if len(rows) <= 1:  # Skip if only header row
#                     continue
                    
#                 # Only process the first data row for building details
#                 for row in rows[1:2]:  # Only get the first data row
#                     cells = row.find_elements(By.TAG_NAME, "td")
#                     if cells:
#                         row_data = [cell.text.strip() for cell in cells]
#                         if len(row_data) >= 4:  # Ensure it has enough data
#                             building_data.append(row_data)
#                             building_headers = headers
#                             logger.info(f"Found building details: {row_data[:3]}...")
#                             return building_headers, building_data
        
#         logger.warning("Could not find building details table")
#         return None, []
#     except Exception as e:
#         logger.error(f"Error extracting building table: {e}")
#         return None, []

# def extract_apartment_details(driver):
#     """Extract ONLY the apartment details table from the page"""
#     try:
#         # Look for tables containing apartment details
#         for xpath in [
#             "//div[contains(text(), 'Apartments/Villas Type Details')]/following::table[1]",
#             "//h4[contains(text(), 'Apartments/Villas Type Details')]/following::table[1]",
#             "//table[.//th[contains(text(), 'Apartment/Villa Type')]]",
#             "//table[.//th[contains(text(), 'Carpet Area')] and .//th[contains(text(), 'Apartment/Villa Type')]]"
#         ]:
#             tables = driver.find_elements(By.XPATH, xpath)
#             if not tables:
#                 continue
                
#             # Process the first matching table
#             table = tables[0]
            
#             # Get headers
#             header_cells = table.find_elements(By.TAG_NAME, "th")
#             if not header_cells:
#                 continue
                
#             headers = [cell.text.strip() for cell in header_cells]
            
#             # Verify this is the apartment details table
#             if not any("Apartment/Villa Type" in header for header in headers):
#                 continue
                
#             # Get data rows
#             rows = table.find_elements(By.TAG_NAME, "tr")
#             if len(rows) <= 1:  # Skip if only header row
#                 continue
                
#             apartment_data = []
#             for row in rows[1:]:  # Process all data rows
#                 cells = row.find_elements(By.TAG_NAME, "td")
#                 if cells:
#                     row_data = [cell.text.strip() for cell in cells]
                    
#                     # Filter valid apartment rows (contains BHK or equivalent)
#                     if (len(row_data) >= 5 and 
#                         not "Total" in " ".join(row_data) and
#                         any(bhk_term in " ".join(row_data) for bhk_term in ["BHK", "Villa", "Apartment"])):
#                         apartment_data.append(row_data)
            
#             if apartment_data:
#                 logger.info(f"Found {len(apartment_data)} apartment details rows")
#                 return headers, apartment_data
        
#         logger.warning("Could not find apartment details table")
#         return None, []
#     except Exception as e:
#         logger.error(f"Error extracting apartment table: {e}")
#         return None, []

# def process_registration_number(driver, reg_number, building_writer, apartment_writer, building_headers_written, apartment_headers_written):
#     logger.info(f"Processing {reg_number}")
#     original_window = driver.current_window_handle
    
#     success = False

#     try:
#         driver.get("https://rera.kerala.gov.in/explore-projects")
#         time.sleep(3)
#         handle_popups(driver)

#         # Find search box and button
#         input_box = wait_for_element(driver, '//*[@id="app"]/div[3]/div/div[1]/div[2]/div/form/div[1]/div[1]/input')
#         search_button = wait_for_element(driver, '//*[@id="app"]/div[3]/div/div[1]/div[2]/div/form/div[3]/button[1]')
        
#         if not input_box or not search_button:
#             logger.error(f"Could not find search elements for {reg_number}")
#             return False, building_headers_written, apartment_headers_written

#         input_box.clear()
#         input_box.send_keys(reg_number)
#         search_button.click()
#         time.sleep(5)

#         # Try to click the project card or more info button
#         more_info_element = None
#         for xpath in [
#             '//*[@id="app"]/div[3]/div/div[3]/a/div[2]/div[3]/span',
#             '//span[contains(text(), "More Info")]',
#             '//div[contains(@class, "project-card")]//span[contains(text(), "More")]'
#         ]:
#             more_info_element = wait_for_element(driver, xpath, timeout=5)
#             if more_info_element:
#                 break
                
#         if more_info_element:
#             try:
#                 more_info_element.click()
#             except:
#                 driver.execute_script("arguments[0].click();", more_info_element)
#             time.sleep(5)
#         else:
#             logger.warning(f"Could not find More Info button for {reg_number}")

#         # Find project details link
#         project_link = None
#         for xpath in [
#             '//*[@id="app"]/div/main/div[2]/div/div[2]/div[1]/div[5]/a[1]',
#             '//a[contains(text(), "Complete Project Details")]',
#             '//a[contains(text(), "Project Details")]'
#         ]:
#             project_link = wait_for_element(driver, xpath, timeout=5)
#             if project_link:
#                 break

#         if not project_link:
#             logger.error(f"Could not find project details link for {reg_number}")
#             return False, building_headers_written, apartment_headers_written

#         try:
#             project_link.click()
#         except:
#             driver.execute_script("arguments[0].click();", project_link)
#         time.sleep(5)

#         # Check if new tab opened and switch to it
#         if len(driver.window_handles) > 1:
#             switch_to_new_tab(driver)

#         # Click on the Construction Progress tab
#         if not click_construction_progress_tab(driver):
#             logger.error(f"Could not find Construction Progress tab for {reg_number}")
#             return False, building_headers_written, apartment_headers_written

#         # Extract building details
#         building_headers, building_data = extract_building_details(driver)
        
#         # Write building details to CSV
#         if building_data:
#             # Write header if it hasn't been written yet
#             if not building_headers_written and building_headers:
#                 building_writer.writerow(["RegistrationNumber"] + building_headers)
#                 building_headers_written = True
                
#             # Write data rows - only the first row for building details
#             building_writer.writerow([reg_number] + building_data[0])
#             logger.info(f"Wrote building details for {reg_number}")
#             success = True

#         # Extract apartment details
#         apartment_headers, apartment_data = extract_apartment_details(driver)
        
#         # Write apartment details to CSV
#         if apartment_data:
#             # Write header if it hasn't been written yet
#             if not apartment_headers_written and apartment_headers:
#                 apartment_writer.writerow(["RegistrationNumber"] + apartment_headers)
#                 apartment_headers_written = True
                
#             # Write data rows
#             for row in apartment_data:
#                 apartment_writer.writerow([reg_number] + row)
#             logger.info(f"Wrote {len(apartment_data)} apartment rows for {reg_number}")
#             success = True

#         # If no data was found
#         if not building_data and not apartment_data:
#             logger.warning(f"No data found for {reg_number}")
#             success = False

#         # Close the new tab if it was opened
#         if len(driver.window_handles) > 1:
#             driver.close()
#             driver.switch_to.window(original_window)

#         return success, building_headers_written, apartment_headers_written

#     except Exception as e:
#         logger.error(f"Error processing {reg_number}: {e}")
#         try:
#             driver.save_screenshot(f"{reg_number}_error.png")
#         except:
#             pass
        
#         # Make sure we return to the original window
#         if len(driver.window_handles) > 1:
#             for handle in driver.window_handles:
#                 if handle != original_window:
#                     driver.switch_to.window(handle)
#                     driver.close()
#             driver.switch_to.window(original_window)
            
#         return False, building_headers_written, apartment_headers_written

# def main():
#     driver = setup_driver()
#     try:
#         with open("input.csv", "r") as infile, \
#              open("building_details.csv", "w", newline="", encoding="utf-8") as building_file, \
#              open("apartment_details.csv", "w", newline="", encoding="utf-8") as apartment_file:

#             csvreader = csv.reader(infile)
#             next(csvreader, None)  # Skip header

#             building_writer = csv.writer(building_file)
#             apartment_writer = csv.writer(apartment_file)
            
#             # Headers will be written when we encounter the first successful registration
#             building_headers_written = False
#             apartment_headers_written = False

#             success, failure = 0, 0
#             for row in csvreader:
#                 if not row: 
#                     continue
                    
#                 reg = row[0].strip()
#                 result, building_headers_written, apartment_headers_written = process_registration_number(
#                     driver, reg, building_writer, apartment_writer, 
#                     building_headers_written, apartment_headers_written
#                 )
                
#                 if result:
#                     success += 1
#                     logger.info(f"Successfully processed {reg}")
#                 else:
#                     failure += 1
#                     logger.warning(f"Failed to process {reg}")

#             logger.info(f"Completed. Success: {success}, Failure: {failure}")

#     finally:
#         driver.quit()

# if __name__ == "__main__":
#     main()






























































import csv
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("rera_scraper.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    # chrome_options.add_argument("--headless")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def wait_for_element(driver, xpath, timeout=20):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
    except TimeoutException:
        logger.error(f"Timeout waiting for element: {xpath}")
        return None

def handle_popups(driver):
    try:
        buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'close')] | //div[contains(@class, 'popup')]//button | //div[contains(@class, 'modal')]//button")
        for button in buttons:
            if button.is_displayed():
                button.click()
                time.sleep(1)
    except Exception as e:
        logger.warning(f"Popup handling error: {e}")

def switch_to_new_tab(driver):
    try:
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        driver.switch_to.window(driver.window_handles[-1])
        WebDriverWait(driver, 20).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        time.sleep(5)
        return True
    except Exception as e:
        logger.error(f"Error switching tab: {e}")
        return False

def click_construction_progress_tab(driver):
    try:
        for xpath in [
            "//a[@href='#tab4']", 
            "//a[contains(text(), 'Construction Progress')]",
            "//ul[contains(@class, 'nav-tabs')]//a[contains(text(), 'Construction')]",
            "//div[contains(@class, 'nav')]//a[contains(text(), 'Construction')]",
            "//li/a[contains(text(), 'Building Progress')]"
        ]:
            tab = wait_for_element(driver, xpath, timeout=5)
            if tab:
                driver.execute_script("arguments[0].scrollIntoView(true);", tab)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(3)
                return True
    except Exception as e:
        logger.error(f"Click tab error: {e}")
    return False

def extract_building_details(driver):
    try:
        building_data = []
        building_headers = []
        
        for xpath in [
            "//div[contains(text(), 'Building Details')]/following::table[1]",
            "//h4[contains(text(), 'Building Details')]/following::table[1]",
            "//div[@id='tab4']//table[1]",
            "//table[.//th[contains(text(), 'Building Name')]]"
        ]:
            table = driver.find_elements(By.XPATH, xpath)
            if table:
                table = table[0]
                
                header_cells = table.find_elements(By.TAG_NAME, "th")
                if not header_cells:
                    continue
                    
                headers = [cell.text.strip() for cell in header_cells]
                
                if not any("Building Name" in header for header in headers):
                    continue
                    
                rows = table.find_elements(By.TAG_NAME, "tr")
                if len(rows) <= 1:
                    continue
                    
                for row in rows[1:2]:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if cells:
                        row_data = [cell.text.strip() for cell in cells]
                        if len(row_data) >= 4:
                            building_data.append(row_data)
                            building_headers = headers
                            logger.info(f"Found building details: {row_data[:3]}...")
                            return building_headers, building_data
        
        logger.warning("Could not find building details table")
        return None, []
    except Exception as e:
        logger.error(f"Error extracting building table: {e}")
        return None, []

def extract_apartment_details(driver):
    try:
        for xpath in [
            "//div[contains(text(), 'Apartments/Villas Type Details')]/following::table[1]",
            "//h4[contains(text(), 'Apartments/Villas Type Details')]/following::table[1]",
            "//table[.//th[contains(text(), 'Apartment/Villa Type')]]",
            "//table[.//th[contains(text(), 'Carpet Area')] and .//th[contains(text(), 'Apartment/Villa Type')]]"
        ]:
            tables = driver.find_elements(By.XPATH, xpath)
            if not tables:
                continue
                
            table = tables[0]
            header_cells = table.find_elements(By.TAG_NAME, "th")
            if not header_cells:
                continue
                
            headers = [cell.text.strip() for cell in header_cells]
            
            if not any("Apartment/Villa Type" in header for header in headers):
                continue
                
            rows = table.find_elements(By.TAG_NAME, "tr")
            if len(rows) <= 1:
                continue
                
            apartment_data = []
            for row in rows[1:]:
                cells = row.find_elements(By.TAG_NAME, "td")
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    if (len(row_data) >= 5 and 
                        not "Total" in " ".join(row_data) and
                        any(bhk_term in " ".join(row_data) for bhk_term in ["BHK", "Villa", "Apartment"])):
                        apartment_data.append(row_data)
            
            if apartment_data:
                logger.info(f"Found {len(apartment_data)} apartment details rows")
                return headers, apartment_data
        
        logger.warning("Could not find apartment details table")
        return None, []
    except Exception as e:
        logger.error(f"Error extracting apartment table: {e}")
        return None, []

def process_registration_number(driver, reg_number, building_writer, apartment_writer,
                                building_headers_written, apartment_headers_written,
                                building_file, apartment_file):
    logger.info(f"Processing {reg_number}")
    original_window = driver.current_window_handle
    success = False

    try:
        driver.get("https://rera.kerala.gov.in/explore-projects")
        time.sleep(3)
        handle_popups(driver)

        input_box = wait_for_element(driver, '//*[@id="app"]/div[3]/div/div[1]/div[2]/div/form/div[1]/div[1]/input')
        search_button = wait_for_element(driver, '//*[@id="app"]/div[3]/div/div[1]/div[2]/div/form/div[3]/button[1]')
        
        if not input_box or not search_button:
            logger.error(f"Could not find search elements for {reg_number}")
            return False, building_headers_written, apartment_headers_written

        input_box.clear()
        input_box.send_keys(reg_number)
        search_button.click()
        time.sleep(5)

        more_info_element = None
        for xpath in [
            '//*[@id="app"]/div[3]/div/div[3]/a/div[2]/div[3]/span',
            '//span[contains(text(), "More Info")]',
            '//div[contains(@class, "project-card")]//span[contains(text(), "More")]'
        ]:
            more_info_element = wait_for_element(driver, xpath, timeout=5)
            if more_info_element:
                break
                
        if more_info_element:
            try:
                more_info_element.click()
            except:
                driver.execute_script("arguments[0].click();", more_info_element)
            time.sleep(5)
        else:
            logger.warning(f"Could not find More Info button for {reg_number}")

        project_link = None
        for xpath in [
            '//*[@id="app"]/div/main/div[2]/div/div[2]/div[1]/div[5]/a[1]',
            '//a[contains(text(), "Complete Project Details")]',
            '//a[contains(text(), "Project Details")]'
        ]:
            project_link = wait_for_element(driver, xpath, timeout=5)
            if project_link:
                break

        if not project_link:
            logger.error(f"Could not find project details link for {reg_number}")
            return False, building_headers_written, apartment_headers_written

        try:
            project_link.click()
        except:
            driver.execute_script("arguments[0].click();", project_link)
        time.sleep(5)

        if len(driver.window_handles) > 1:
            switch_to_new_tab(driver)

        if not click_construction_progress_tab(driver):
            logger.error(f"Could not find Construction Progress tab for {reg_number}")
            return False, building_headers_written, apartment_headers_written

        building_headers, building_data = extract_building_details(driver)
        if building_data:
            if not building_headers_written and building_headers:
                building_writer.writerow(["RegistrationNumber"] + building_headers)
                building_file.flush()
                building_headers_written = True
                
            building_writer.writerow([reg_number] + building_data[0])
            building_file.flush()
            logger.info(f"Wrote building details for {reg_number}")
            success = True

        apartment_headers, apartment_data = extract_apartment_details(driver)
        if apartment_data:
            if not apartment_headers_written and apartment_headers:
                apartment_writer.writerow(["RegistrationNumber"] + apartment_headers)
                apartment_file.flush()
                apartment_headers_written = True
                
            for row in apartment_data:
                apartment_writer.writerow([reg_number] + row)
                apartment_file.flush()
            logger.info(f"Wrote {len(apartment_data)} apartment rows for {reg_number}")
            success = True

        if not building_data and not apartment_data:
            logger.warning(f"No data found for {reg_number}")
            success = False

        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(original_window)

        return success, building_headers_written, apartment_headers_written

    except Exception as e:
        logger.error(f"Error processing {reg_number}: {e}")
        try:
            driver.save_screenshot(f"{reg_number}_error.png")
        except:
            pass
        
        if len(driver.window_handles) > 1:
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.switch_to.window(handle)
                    driver.close()
            driver.switch_to.window(original_window)
            
        return False, building_headers_written, apartment_headers_written

def main():
    driver = setup_driver()
    try:
        with open("input.csv", "r") as infile, \
             open("building_details.csv", "w", newline="", encoding="utf-8") as building_file, \
             open("apartment_details.csv", "w", newline="", encoding="utf-8") as apartment_file:

            csvreader = csv.reader(infile)
            next(csvreader, None)  # Skip header

            building_writer = csv.writer(building_file)
            apartment_writer = csv.writer(apartment_file)
            
            building_headers_written = False
            apartment_headers_written = False

            success, failure = 0, 0
            for row in csvreader:
                if not row:
                    continue
                    
                reg = row[0].strip()
                result, building_headers_written, apartment_headers_written = process_registration_number(
                    driver, reg, building_writer, apartment_writer,
                    building_headers_written, apartment_headers_written,
                    building_file, apartment_file
                )
                
                if result:
                    success += 1
                    logger.info(f"Successfully processed {reg}")
                else:
                    failure += 1
                    logger.warning(f"Failed to process {reg}")

            logger.info(f"Completed. Success: {success}, Failure: {failure}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
