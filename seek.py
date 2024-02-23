import requests
from bs4 import BeautifulSoup
import time
from requests_html import HTMLSession
import re
import json
from google_sheet import GoogleSheet
import settings as config

# Google Sheet Object
gs_obj = GoogleSheet()

worksheet = gs_obj.worksheet(config.seek["sheet_id"], config.seek["sheet_title"])

class Seek: 
    def __init__(self):
        self.jobs_url = []

    def getJobLinks(self, baseUrl, urlPath, pageNo):
        jobUrls = []
        try:
            if pageNo == 1:
                r = requests.get(baseUrl + urlPath)
                print("\n--> WEBSITE URL: ", baseUrl+urlPath)
            else:
                r = requests.get(baseUrl + urlPath + "?page=" + str(pageNo))
                print("\n--> WEBSITE URL: ", baseUrl+urlPath+"?page="+str(pageNo))
        except:
            time.sleep(5)
            # AGAIN REQUEST IF ANY ERROR
            print("\nRETRYING TO GET JOBS LINKS!\n")
            if pageNo == 1:
                r = requests.get(baseUrl + urlPath)
            else:
                r = requests.get(baseUrl + urlPath + "?page=" + str(pageNo))

        if r.status_code == 200:
            soup = BeautifulSoup(r.content, features="html.parser")
            links = soup.select(".y735df0.y735dff.y735df0.y735dff._1iz8dgs5i._1iz8dgsj._1iz8dgsk._1iz8dgsl._1iz8dgsm._1iz8dgs7")
            for link in links:
                href = link.get("href")
                if href:
                    jobUrls.append(baseUrl+href)
                    
            return jobUrls
        else:
            print("ERROR WHILE SCRAPING JOBS LINKS: ", r.status_code)

    def scrape_job(self, job_url, profession):

        print("\nSCRAPPING START: ", job_url)
        title=''
        companyName=''
        jobType=''
        location=''
        listedAt=''
        contactName=''
        email=''
        phone=''
        try:
            job_page = requests.get(job_url)
        except:
            # AGAIN REQUEST IF ANY ERROR
            print("\nRETRYING TO GET JOB'S RECORD!\n")
            job_page = requests.get(job_url)

        
        if job_page.status_code == 200:
            soup = BeautifulSoup(job_page.content, features="html5lib")
            
            try:
                title = soup.select_one('[data-automation="job-detail-title"]').getText().strip()
            except Exception as error:
                print("JOB TITLE NOT EXIST: ", error)
            
            try:
                companyName = soup.select_one('[data-automation="advertiser-name"]').getText().strip()
            except Exception as error:
                print("Company Name NOT EXIST: ", error)

            try:
                jobType = soup.select_one('[data-automation="job-detail-work-type"]').getText().strip()
            except Exception as error:
                print("JOB TYPE NOT EXIST: ", error)
            
            try:
                res = soup.find('script', {'data-automation': 'server-state'})
                # Search for the variable value using regular expression
                pattern = r'window\.SEEK_REDUX_DATA\s*=\s*({.*?});'
                match = re.search(pattern, res.contents[0])

                # Check if a match is found and extract the variable value
                if match:
                    seek_redux_data = match.group(1)
                        
                    # location
                    matchLocation = re.search(r'"location":\s*(\{[^}]+\})', seek_redux_data)
                    if matchLocation:
                        location_json = matchLocation.group(1)
                        location = json.loads(location_json)["label"]

                    
                    # Listed
                    matchListedAt = re.search(r'"listedAt":\s*(\{[^}]+\})', seek_redux_data)
                    if matchListedAt:
                        listedAt_json = matchListedAt.group(1)
                        listedAt = json.loads(listedAt_json)["shortLabel"]

            except Exception as error:
                print("JOB LOCATION OR LISTED DATE NOT EXIST: ", error)
            
            try:
                session = HTMLSession()
                response = session.get(job_url)
                response.html.render(timeout=20)
                contact = response.html.find('[data-automation="jobAdDetails"]')
                phone_pattern = r"\(?\d{2}\)?\s?\d{4}\s?\d{4}|\d{4}\s?\d{3}\s?\d{3}|\d{8}"



                for i in contact:
                    # Remove parentheses and spaces from the phone number
                    cleaned_number = re.sub(r'[()]', '', i.text)
                    # match variable contains a Match object.
                    phone = re.findall(phone_pattern, cleaned_number) 
                    if phone:
                        phone = ', '.join(phone)
                    else:
                        phone = ''
                    email_pattern = r'[\w.-]+@[\w.-]+\.\w+\b'
                    mail = re.findall(email_pattern, i.text)
                    if mail:
                        email=', '.join(map(str,mail))
                    else:
                        email = ''
            except Exception as error:
                print("Phone & Email not found: ", error)

            # Contact Name from email
            try:
                if email != '':
                    email_list = email.split(",")
                    for em in email_list:
                        match = re.match(r'([^@]+)@', em)
                        if match:
                            contactName =contactName + " " + match.group(1)
            except Exception as error:
                print("Contant Name not found: ", error)


            try:
                job={
                    "Job URL": job_url,
                    "Job Site": "Australian Seek Association",
                    "Title": title,
                    "Company Name": companyName,
                    "Type": jobType,
                    "Location": location,
                    "Contact Name": contactName,
                    "Email": email,
                    "Phone": phone,
                    "Listed": listedAt,
                    "Profession": profession
                }

                # Saving to Google Sheet
                if email != '':
                    gs_obj.add(worksheet, list(job.values()))
                else:
                    print("\nEmail not exist so skipped this job: ", job["Job URL"])
            except Exception as error:
                print("No Saved to Google Sheet !", error)
        
    def scrape(self, baseUrl, category, singlePage=0, pageFrom=0, pageTo=0):
        urlPath = "/" + category
        profession = category.split("-jobs")[0]
        if pageFrom > 0 and pageTo > 0:
            count = 1
            for pageNo in range(pageFrom, pageTo+1):
                jobLinks = []
                jobLinks = self.getJobLinks(baseUrl, urlPath, pageNo)
                print(f"\n--> TOTAL JOBS ON PAGE: {pageNo} = {len(jobLinks)}")
                
                # scrape jobs
                for url in jobLinks: 
                    job={"Job URL" : url}
                    # If already exist in Google Sheet then ignore
                    isExist=gs_obj.isExist(worksheet, job)
                    if isExist:
                        print("\n--> JOB ALREADY EXIST : ", job["Job URL"])
                    else:
                        self.scrape_job(job["Job URL"], profession)
                    print("\n--> TOTAL COMPLETED: ", count)
                    count +=1
        else:
            jobLinks = []
            count = 1
            jobLinks = self.getJobLinks(baseUrl, urlPath, singlePage)
            print(f"\n--> TOTAL JOBS ON PAGE: {singlePage} = {len(jobLinks)}")
            
            # scrape jobs
            for url in jobLinks: 
                job={"Job URL" : url}
                # If already exist in Google Sheet then ignore
                isExist=gs_obj.isExist(worksheet, job)
                if isExist:
                    print("\n--> JOB ALREADY EXIST : ", job["Job URL"])
                else:
                    self.scrape_job(job["Job URL"], profession)
                print("\n--> TOTAL COMPLETED: ", count)
                count +=1
