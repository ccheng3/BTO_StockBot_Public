# BTO_Stock_Bot
BillionToOne Clinical Laboratory Fast-Moving Consumable Webscraper Bot 

### Purpose: 
Selenium Webdriver script that webscrapes BTO Stock-Boss data. Updates 'weekly inventory check on fast moving stock' - main goal is to proactively catch fast moving stock at low quantity so #supply-chain channel members can purchase more ASAP + confirm current BTO standing orders with ULS and external suppliers.

### Notes:
Q5 HOT START MM (501959358) and all Illumina items are edge cases; Q5's VMI Stockroom count is 
actually PRE + VMI count while all Illumina items' VMI Stockroom count is actually POST + VMI count. 

Monthly Usage column scrapes the previous month's usage value, but isn't used to calculate the 1.5 month buffer value. The spreadsheet uses Kitty's calculated monthly usage values and the spreadsheet highlights items that have a scraped usage value that is > 30% than Kitty's usage value. (Lab uses 30% more of the item than what the current monthly usage says.)

#### 12/16/2021:
 Most fragile part of the script is the hardcoding of the Google spreadsheet's Columns. Currently not sure if there's a dynamic solution for this. The situation: We'll take the "Current VMI Stockroom Stock Quantity" column (AI) as an example. The script currently inserts the newly scraped quantity values to column AI, but the problem is that "AI" is hardcoded into the script. Therefore, if a new column is inserted, then column AI will be pushed. If the new column is inserted to the left of column AI, then AI becomes AJ and so on to the right. Same reasoning if new column is inserted to the right. And so you need to manually update the new column name in the script. Currently just remembering to manually update when new column is added.  

 Monthly usage values - HTML td element offset values --> January has index val 15, December has index val 26, with increments of 1 for all months in between. Check line 172 (try except block).
 Used an f-string with the calculated month's td cell number in the get_element_by_xpath(). 

## Secondary Project: Eppendorf Eppoints Redemption Bot 
### Purpose: 
The Eppoints Bot automates the laborious task of manually redeeming Eppendorf consumable points. Also uses Selenium WebDriver and ezsheets Python module. 

12/18/2021: This version does not handle invalid codes (codes that have already been redeemed but were scanned into the spreadsheet again) and will crash after invalid code detection. 

12/30/2021: Added new functionality to account for full URL codes to parse AND hand-entered codes (due to stickers stuck to each other for far too long and rendering QR code unable to scan). Scannable codes go into Column B, unscannable codes
go into Column C. 