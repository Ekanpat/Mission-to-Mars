# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import lxml
import datetime as dt
# from webdriver_manager.chrome import ChromeDriverManager
from flask import Flask 


def scrape_all():
    # Initiate headless driver for deployment
    # Set the executable path and initialize the chrome browser in splinter
    browser = Browser("chrome", executable_path="C:\Program Files (x86)\chromedriver", headless=True)

    # # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "mars_hemi": mars_hemi(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def mars_hemi(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
        
    #HTML Object.
    html = browser.html
    astro_soup = soup(html, "html.parser")

    # Store main URL in a variable for iteration
    main_url = "https://astrogeology.usgs.gov"
    # Executing some stuff and assigning variables to images and titles
    images = astro_soup.find("div", class_="collapsible results")
    titles = astro_soup.find('h3').text
    # Creating a  temporary list to hold the specific image urls
    hemisphere_urls = []
    all_images = images.find_all('div', class_ = 'description')
    # looping through to collect all the images and links
    for hem in all_images:
        hem_url = hem.find('a')['href']
        hemisphere_urls.append(hem_url)
    hemi_url = main_url+'hem_url'
    hemisphere_image_urls = []
# for hemi in hemisphere_urls:
    for hemi in hemisphere_urls:
    # Creating an empty dictionary
        hemisphere = {}
        hemi_url = main_url + hemi
    # Run init_browser/driver.
        browser.visit(hemi_url)
        html = browser.html
        hemi_soup = soup(html, "html.parser")
    ## Retrieve the full-resolution image URL
    image = hemi_soup.find('img', class_="wide-image")['src']
    ## Retrieve the titles
    titles = browser.find_by_css("h2.title").text
    # Saving the full-resolution image URL string
    hemisphere['img_url'] = main_url + image
    # Saving the the hemisphere image title as string
    hemisphere['title'] = titles
    hemisphere_image_urls.append(hemisphere)
    # print(datetime.datetime.now() - begin_time)

    return hemisphere_image_urls
    
if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())