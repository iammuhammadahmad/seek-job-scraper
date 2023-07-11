from seek import Seek
import logging
import sys

def robotInfo():
    print("\n")
    print("       ===============================================================")
    print("       =               WELCOME TO Job SCRAPER :-)                    =")
    print("       = ----------------------------------------------------------- =")
    print("       = VERSION: 1.00                                               =")
    print("       = DATE: Jun 25, 2023                                          =")
    print("       = DEVELOPER : MUHAMMAD AHMAD                                  =")
    print("       = heremuhammadahmad@gmail.com                                 =")
    print("       ===============================================================")
    print("\n\n")
    print("-------->>> JOB SCRAPER START... :-)\n")


def menu():
    print("FOLLOWING SITES ARE AVAILABLE TO SCRAPES!\n")
    print("1: www.seek.com.au")

def jobCategory():
    print("FOLLOWING Category ARE AVAILABLE TO SCRAPES!\n")
    print("1: psychologist-jobs")
    print("2: podiatrist-jobs")
    print("3: physiotherapist-jobs")
    print("4: occupational-therapist-jobs")
    print("5: chiropractic-jobs")
    print("6: speech-pathologist-jobs")

if __name__ == '__main__':
    start = True
    robotInfo()
    while start:
        baseUrl="https://www.seek.com.au"
        category=""  
        singlePage = 0
        pageRange = 0
        pageFrom = 0
        pageTo = 0
        seek_obj = Seek()
        menu()
        scrapeSite = int(input("\n-> SELECT SITE TO SCRAPE: "))

        if scrapeSite == 1:
            # Print available categories
            jobCategory()

            # Select category
            selectCategory = int(input("\n-> SELECT CATEGORY TO SCRAPE: "))

            if selectCategory <= 6 and selectCategory >= 1:
                if selectCategory == 1:
                    category = "psychologist-jobs"
                if selectCategory == 2:
                    category = "podiatrist-jobs"
                if selectCategory == 3:
                    category = "physiotherapist-jobs"
                if selectCategory == 4:
                    category = "occupational-therapist-jobs"
                if selectCategory == 5:
                    category = "chiropractic-jobs"
                if selectCategory == 6:
                    category ="speech-pathologist-jobs"

            else:
                print("INVALID CATEGORY!")
                sys.exit()
            
            print("\n-- NOTE: MAKE SURE TOTAL NO OF PAGE EXIST!")
            totalPage = int(input("\n-> TOTAL PAGE: "))
            
            if totalPage <= 0:
                logging.error('Total page should be greater than 0 !')
                sys.exit()

            option = int(input('\n-> If you want to scrape single page then enter (1) OR (2) for Multi Page: '))
            print("\n-- SLECTED OPTION: ", option)
            if option != 1 and option !=2: 
                logging.error('INVALID OPTION!')
                sys.exit()

            # Single Page
            if option == 1:
                singlePage = int(input("\n-> Enter PAGE NO: "))
        
                if singlePage <=0 and singlePage > totalPage:
                    logging.error('INVALID PAGE NO!')
                    sys.exit()

                seek_obj.scrape(baseUrl, category, singlePage, 0, 0)
                
            
            # Multi Page
            if option == 2:
                pageRange = input(f"\n-> Enter PAGE IN RANGE (i.e. 1-{totalPage}): ")
                pageFrom = int(pageRange.split('-')[0])
                pageTo = int(pageRange.split('-')[-1])
    
                if (pageFrom <= 0 or pageFrom >= totalPage or pageFrom >= pageTo) or (pageTo < 0 or pageTo <= pageFrom or pageTo > totalPage):
                    logging.error(f'INVALID PAGE Range ({pageFrom}-{pageTo})')
                    sys.exit()
                seek_obj.scrape(baseUrl, category,0, pageFrom, pageTo)

        isRun = input("\n--> DO YOU WANT TO RUN AGAIN THEN WRITE (yes)? TO CANCEL PRESS ANY KEYWORD: ")

        if isRun == 'yes':
            pass
        else:
            sys.exit()
               
               



