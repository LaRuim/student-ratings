from selenium import webdriver
from time import sleep
from csv import writer

IS_OUTPUT_CSV = False
scoreboard_url = "https://codingcompetitions.withgoogle.com/kickstart/round/0000000000050eda"

chromeOptions = webdriver.ChromeOptions()
prefs = {'profile.managed_default_content_settings.images': 2,  # does not load images on web page
         'disk-cache-size': 1024}  # use disk cache to reduce page load time

chromeOptions.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chromeOptions)
driver.get(scoreboard_url)



'''
<div class="ranking-table__row">
    <div class="ranking-table__row-cell ranking-table__row-cell--left ranking-table__row-cell__rank">1</div>
        <div class="ranking-table__row-cell ranking-table__row-cell--left ranking-table__row-cell__displayname">
            <a href="/codejam/submissions/00000000000000cb/eTAxMDV3NDk" class="ranking-table__row-cell__submissions_link">
                <p><img src="/static/Canada-20.png" class="ranking-table__row-cell-flag flag has-tooltip" />y0105w49 </p>                                    
            </a>
        </div>
    <div class="ranking-table__row-cell ranking-table__row-cell--left ranking-table__row-cell__score">
        <span class="user-total-score">100</span>
    </div>
</div>


Each record in the scoreboard is of this format.
Rank is stored directly in the <div> with className="ranking-table__row-cell__rank"
Score is stored directly in the <span> with className="user-total-score"
UserName is stored in a <p> which is the child element of the <a> with className="ranking-table__row-cell__displayname"

'''


score_class = "user-total-score"
rank_class = "ranking-table__row-cell__rank"
name_class = "ranking-table__row-cell__displayname"
scraped_scoreboard = list()

# Wait for scoreboard to load
while not driver.find_elements_by_class_name(score_class):
    sleep(1)

input()
'''Pause while user changes default page view to 20 rows - useful for large scoreboard size
Make necessary changes in page, press enter to continue...'''

# Find number of pages in the scoreboard
total_pages = int(driver.find_element_by_class_name("ranking-table-page-number-total-pages").text.split()[1])


for page in range(total_pages):
    score_elements = driver.find_elements_by_class_name(score_class)
    rank_elements = driver.find_elements_by_class_name(rank_class)[1:]
    name_elements = driver.find_elements_by_class_name(name_class)
    scraped_scoreboard.extend(list(zip(
        [x.find_element_by_tag_name("p").text for x in name_elements],
        [y.text for y in rank_elements],
        [z.text for z in score_elements])))
    if page == total_pages-1:  # Reached last_page
        break
    driver.find_elements_by_tag_name("button")[-1].click()  # click to go to next page
    last_name = scraped_scoreboard[-1][0]
    while driver.find_elements_by_class_name(name_class)[-1].find_element_by_tag_name("p").text == last_name:
        sleep(0.1)  # Wait until next page has loaded

driver.close()

if IS_OUTPUT_CSV:
    with open(f"{scoreboard_url.split('/')[-1]}.csv", "w") as fp:
        csv_writer = writer(fp)
        csv_writer.writerows(scraped_scoreboard)
else:
    print(*[x[0] for x in scraped_scoreboard], sep="\n")
