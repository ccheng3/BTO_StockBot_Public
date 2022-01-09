#!/usr/bin/python3
# Author: Chris Cheng, CLA, BillionToOne
# Date: 11/21/2021

from os import link
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pyinputplus as pyip
import time
from datetime import datetime
from datetime import date
import requests
import sys
import ezsheets


def move_to_store_room(storeroom_name: str):
    """
    Move the webpage to the specified store room.
    Applicable store rooms are:
    - POST LAB POU 3
    - PRE LAB POU 1
    - VMI STOCKROOM
    EDIT 12/11/21 --> Kevin added new "In-House Stockroom" - what is this?
    """
    store_object = Select(browser.find_element_by_id(
        'ctl00_ContentMain1_ddlSearchStore'))
    store_object.select_by_value(storeroom_name)
    # stock_levels_search_Run_btn = browser.find_element_by_id(
    #     'ctl00_ContentMain1_btnApplyFilter')
    # stock_levels_search_Run_btn.click()
    click_Run_button('ctl00_ContentMain1_btnApplyFilter')


def click_Run_button(btn_id: str):
    """
    Click the "Run" button in the specified nav bar link's search filter form
    """
    stock_levels_search_Run_btn = browser.find_element_by_id(f"{btn_id}")
    stock_levels_search_Run_btn.click()


def log_in_to_StockBoss():
    """
    Log into StockBoss with your credentials.
    """
    # browser.maximize_window() ---> seemed interesting at first but not as useful for a webscraper script.
    # log in to Stock-Boss
    usernameElem = browser.find_element_by_id('ctl00_ContentMain1_txtUserName')
    usernameElem.send_keys('USERNAME_GOES_HERE')
    passwordElem = browser.find_element_by_id('ctl00_ContentMain1_txtPassword')
    # I don't think that this is such a big security issue for such a small project used internally. (only me)
    # But pyinputplus does work - will wait for you to input the password on the command line in secure asterisk
    # format.
    # passwordElem.send_keys(pyip.inputPassword())
    passwordElem.send_keys('PASSWORD_GOES_HERE')
    # passwordElem.submit()
    # This is actually the more tedious way of logging in lol.
    browser.find_element_by_id('ctl00_ContentMain1_btnLogin').click()

    # choose the Menlo Park site
    browser.find_element_by_id(
        'ctl00_ContentMain1_ASPxRoundPanel3_RadioButtonList1_0').click()
    # need to wait for "Apply" button to be available before initiating the click. (small detail that I missed - similar to awaiting
    # the dropdown list to appear after entering in the Eppoint redemption code into the input field.)
    time.sleep(1)
    browser.find_element_by_id(
        'ctl00_ContentMain1_ASPxRoundPanel3_btnApply').click()

    time.sleep(2)
    move_to_nav_bar_link(4, 'Manage Stock')


def move_to_nav_bar_link(nav_bar_element_index: int, nav_bar_element_link: str):
    """
    Moves to the requested nav bar, then the specified link within.
    """
    stock_nav_element = browser.find_element_by_xpath(
        f"/html[@class='dxChrome dxMacOSPlatform dxWebKitFamily dxBrowserVersion-96']/body[@id='pagebody']/form[@id='aspnetForm']/div[@id='divContainer']/table/tbody/tr[2]/td/table/tbody/tr/td[1]/ul[@id='ctl00_ASPxNavBar1']/li[@id='ctl00_ASPxNavBar1_GR{nav_bar_element_index}']")
    stock_nav_element.click()
    time.sleep(2)
    browser.find_element_by_link_text(f"{nav_bar_element_link}").click()

# current_year, current_month, current_day = str(date.today()).split('-')


def configure_monthly_usage_val_params(current_year: str, current_month: str, current_day: str) -> int:
    """
    Determine the monthly usage parameters using current date and filter to VMI Stockroom,
    then also filter to previous year's data if needed.
    Return the previous month's td element cell index.
    """
    previous_month = 12 if current_month == '01' else int(current_month) - 1
    # initialize flag to check for edge case - move to previous year for previous month's usage vals
    is_current_month_January = True if current_month == '01' else False
    # monthly usage table - HTML td element's indexing offset (check the HTML again to see what I mean)
    previous_month_cell_index = previous_month + 14
    move_to_nav_bar_link(5, 'Usage / Value Report')
    time.sleep(1)
    move_to_store_room('VMI_STOCKROOM')
    # select previous year in select dropdown menu if flag is True
    # For example, if current year is 2021, then we want to select 2020 to view Dec. 2020's usage vals.
    if is_current_month_January:
        year_object = Select(browser.find_element_by_id(
            'ctl00_ContentMain1_ddlYear'))
        year_object.select_by_value(f"{int(current_year) - 1}")
    time.sleep(2)
    return previous_month_cell_index


def enter_part_number(part_num: str):
    """
    Enter the new part number into the 'Part / Desc.' field.
    """
    part_number_field = browser.find_element_by_id(
        'ctl00_ContentMain1_txtSearchPn')
    part_number_field.click()
    part_number_field.clear()
    part_number_field.click()
    part_number_field.send_keys(part_num)


def return_total_count(supplier_name: str, part_num: str, stock_quant_value: str) -> int:
    """
    Calculate and return the total quantity count if the item is Q5 or an 
    Illumina item. 
    """
    second_quant_value = 0
    if part_num == '501959358':
        move_to_store_room('PRE_LAB_POU_1')
        second_quant_value = browser.find_element_by_xpath(
            stock_element_xpath).text
    if supplier_name == 'Illumina':
        move_to_store_room('POST_LAB_POU_3')
        second_quant_value = browser.find_element_by_xpath(
            stock_element_xpath).text
    return int(stock_quant_value) + int(second_quant_value)


start = time.time()
browser = webdriver.Chrome('/usr/local/bin/chromedriver')
browser.get('https://billiontoone.stock-boss.com/')
log_in_to_StockBoss()
# filter the inventory to VMI Stockroom only ---> I can manually check Overstock 112 counts b/c only like 4-5 items to check
move_to_store_room('VMI_STOCKROOM')
# Use the part number and iterate through search and scrape the new quantity count
# For now, I'll store the scraped data in a new Google Sheet; 2 columns, column 1 is part number, column 2 is quantity count.

# use 'ezsheets' module to update Kitty's 'fast moving stock' spreadsheet
# *** It looks like ezsheets allows you to directly update the spreadsheet.
# Therefore, I don't actually need to download the spreadsheet.
# 1) Scrape the updated stock quantity values
# 2) Directly update the spreadsheet from the script.
ss = ezsheets.Spreadsheet('GOOGLE_SPREADSHEET_UNIQUE_ID_GOES_HERE')
fast_moving_stock_sheet = ss.sheets[0]
# row one is the title and not an item so we don't include it, and Python range() stops before end index.
# this for loop condition is the reason why no blank rows on the bottom of spreadsheet can exist - rowCount also takes any
# blank rows into its count, which we don't want.
for index in range(2, fast_moving_stock_sheet.rowCount + 1):
    total_count = 0
    move_to_store_room('VMI_STOCKROOM')
    # grab each part number
    part_num = fast_moving_stock_sheet[f'A{index}']
    # scrape each part num's current stock quantity.
    enter_part_number(part_num)
    click_Run_button('ctl00_ContentMain1_btnApplyFilter')
    stock_element_xpath = "/html[@class='dxChrome dxMacOSPlatform dxWebKitFamily dxBrowserVersion-96']/body[@id='pagebody']/form[@id='aspnetForm']/\
        div[@id='divContainer']/table/tbody/tr[2]/td/table/tbody/tr/td[4]/div[@class='PNormal']/div[@id='ctl00_ContentMain1_divContent']\
        /div[@id='ctl00_ContentMain1_UpdatePanel1']/div[4]/table[@id='ctl00_ContentMain1_GridView1']/tbody/tr[2]/td[13]/itemstyle/table/tbody/tr/td[1]"
    stock_quant_value = browser.find_element_by_xpath(stock_element_xpath).text
    # update the item's current stock quant in the spreadsheet
    # check for Q5 HotStart and Illumina items edge cases, respectively.
    # (Q5 = VMI + PRE counts and Illumina items = VMI + POST counts)
    supplier_name = fast_moving_stock_sheet[f'F{index}']
    fast_moving_stock_sheet[f'AI{index}'] = return_total_count(
        supplier_name, part_num, stock_quant_value)


# ss = ezsheets.Spreadsheet('1FvEBuAPesEK5jDAn4dEYAffzfFH3ljfNbl5o7S2Dz5k')
# fast_moving_stock_sheet = ss.sheets[0]
# scrape monthly usage values for the previous month if it's a new month.
current_year, current_month, current_day = str(date.today()).split('-')
if current_day == '01':
    prev_month_cell_index = configure_monthly_usage_val_params(
        current_year, current_month, current_day)

    for index in range(2, fast_moving_stock_sheet.rowCount + 1):
        part_num = fast_moving_stock_sheet[f'A{index}']
        # scrape each part num's previous month's usage value.
        # if usage value is missing (like RNAse A and Q5 Hot Start, then insert a -5000 placeholder)
        # otherwise insert the scraped usage value into the spreadsheet for comparison with
        # Kitty's calculated values.
        enter_part_number(part_num)
        click_Run_button('ctl00_ContentMain1_btnApplyFilter')
        # scrape the value and insert into spreadsheet.
        previous_month_usage_value = 0
        try:
            previous_month_usage_value = browser.find_element_by_xpath(
                f"/html[@class='dxChrome dxMacOSPlatform dxWebKitFamily dxBrowserVersion-96']/body[@id='pagebody']/form[@id='aspnetForm']/div[@id='divContainer']/table/tbody/tr[2]/td/table/tbody/tr/td[4]/div[@class='PNormal']/div[@id='ctl00_ContentMain1_divContent']/div[@id='ctl00_ContentMain1_UpdatePanel1']/div[@id='ctl00_ContentMain1_divConsumptionReport']/div[@id='ctl00_ContentMain1_divReportResults']/div/table[@id='ctl00_ContentMain1_GridView1']/tbody/tr[2]/td[{prev_month_cell_index}]").text
        except NoSuchElementException:
            previous_month_usage_value = -5000
        if previous_month_usage_value == '':
            previous_month_usage_value = 'EMPTY VALUE!'
        fast_moving_stock_sheet[f'AG{index}'] = previous_month_usage_value


# quit the web browser after script successfully finishes running.
# Ok ---> this command does not work if the driver runs into error/exception
# Therefore, when error/exception is encountered need to try/except it into its own block
# and handle inside.
browser.quit()
end = time.time()
print(end - start)

now = datetime.now()
# make a note in the script to create a new file
file1 = open("/Users/ccheng/Desktop/MyFile.txt", "a")
file1.write(f"This script last ran {now}")
file1.close()
