import sys
import os
from utils import selenium_utils, log
from selenium.common.exceptions import ElementClickInterceptedException
driver = selenium_utils.make_driver()  
load_all = selenium_utils.load_all(driver)
load = selenium_utils.load(driver)

"""
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

"""

base_url = r'https://codingcompetitions.withgoogle.com'
country_filter = r'?scoreboard_type=India'
score_class = r'user-total-score'
rank_class = r'ranking-table__row-cell__rank'
name_class = r'ranking-table__row-cell__displayname'
dropdown_xpath = r'//*[@id="scoreboard"]/div[2]/div/div[2]/div[2]/div/div'
dropdown_vals_class = r'mdc-list-item'
last_page_class = r'ranking-table-page-number-total-pages'
next_button_xpath = r'//*[@id="scoreboard"]/div[2]/div/div[2]/div[3]/button[2]'

def get_contest_scoreboard(contest_name):
    contest_type = contest_name[0]
    contest_round = contest_name[1].upper()
    year = contest_name[-1]
    schedule_url = f'{base_url}/{contest_type}/archive/{year}'
    log.info(f'Getting {schedule_url}')
    driver.get(schedule_url)
    rows = load_all(r'//div[@role="cell"]', 'xpath')
    name = f'Round {contest_round} {year}'
    log.info(f'Finding {name}')
    for row in rows:
        if row.text == name:
            scoreboard_url = str(row.find_element_by_tag_name('a').get_attribute('href'))
            return scoreboard_url

def scrape(contest_names):
    final_scoreboard = list()
    leaderboards = []
    for contest_name in contest_names:
        driver.get(get_contest_scoreboard(contest_name))
        #driver.get(get_contest_scoreboard(contest_name) + country_filter)
        #load_all(r'mdc-button__label', 'class')
        #driver.refresh()

        load(dropdown_xpath, 'xpath').click()
        load_all(dropdown_vals_class, 'class')[-1].click()

        # Find number of pages in the scoreboard
        last_page = int(load(last_page_class, 'class').text.split()[-1])
        last_score = "1"

        for page in range(0, last_page):
            try:
                score_elements = load_all(score_class, 'class')
                rank_elements = load_all(rank_class, 'class')
                name_elements = load_all(name_class, 'class')
                final_scoreboard.extend(list(zip(
                    [x.find_element_by_tag_name("p").text for x in name_elements],
                    [y.text for y in rank_elements],
                    [z.text for z in score_elements])))
            except:
                score_elements = load_all(score_class, 'class')
                rank_elements = load_all(rank_class, 'class')[1:]
                name_elements = load_all(name_class, 'class')
                final_scoreboard.extend(list(zip(
                    [x.find_element_by_tag_name("p").text for x in name_elements],
                    [y.text for y in rank_elements],
                    [z.text for z in score_elements])))
            try:
                load(next_button_xpath, 'xpath').click()
            except ElementClickInterceptedException: # When unable to click next button
                log.info(f'Last Page (page {last_page + 1}) reached')
        shared_rank = []
        rank_list = []
        for user in final_scoreboard:
            if user[1] == last_score:
                shared_rank.append(user[0])
                if final_scoreboard.index(user) == len(final_scoreboard) - 1:
                    rank_list.append(' '.join(shared_rank))
            else:
                rank_list.append(' '.join(shared_rank))
                shared_rank = []
                last_score = user[1]
                shared_rank.append(user[0])
        leaderboards.append(rank_list)
    return leaderboards