#!/usr/bin/env python3

"""Retrieve past exam papers from the DCU web page"""

## imports

# standard library
import os
import os.path
import sys
import time

# selenium core
import selenium # selenium.__version__ for version info
from selenium import webdriver

# selenium specific
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


## version info
selenium_version = selenium.__version__


## global settable variables

env = {}

paths = {
    'driver': '../tools/geckodriver.exe',
    'save_dir': os.getcwd(),
}

urls = {
    'main': 'https://www.dcu.ie/registry/past-exam-papers.shtml',
    'dl_root': 'https://drive.google.com/file/d/', 
}

css_sels = {
    'paperdata' :'#mySelection_wrapper',
    'howmany' :'#mySelection_length select',
    'modfilter' :'#mySelection_filter input',
    'sort_s' :'#mySelection > thead > tr > th', 
    'next' :'#mySelection_next',
    'prev' :'#mySelection_previous',
    'popupbutton' :'#sliding-popup button',
    'infodatum' :'#mySelection_info',
    'paper_s' :'#mySelection > tbody > tr:nth-of-type({})',
    'paper_link' : 'td.sorting_1 > a', 
    'paper_data_s': 'td',

    'dldata': "div[role='document']",
    'dlbutton' : "div[aria-label='Download']",
}


## decorators

def on(url):
    """Raises an error if the browser is not on the required url"""
    raise NotImplementedError

def on_root(root_url):
    """Requires the page the browser is on to have the same 'base' URL as the specified root_url"""
    raise NotImplementedError


## exceptions

class NotEnoughArgumentsError(TypeError):
    """The number of arguments received at the command-line via sys.argv does not match the required number of arguments"""
    pass


## core classes

class DCU_Website(webdriver.Firefox):
    """Wrappers around elements, functions, and actions on a DCU papers web page
    Instance methods return web elements or have a side effect on the browser instance
    Static methods include website related functionalities like returning appropriate profile preferences for a browser"""

    def __init__(self, firefox_profile=None, firefox_binary=None, timeout=30, capabilities=None, proxy=None, executable_path='geckodriver', options=None, log_path='geckodriver.log', firefox_options=None, service_args=None, 
        wait_time=15, sliding_time=20):
        super().__init__(firefox_profile=firefox_profile, firefox_binary=firefox_binary, timeout=timeout, capabilities=capabilities, proxy=proxy, executable_path=executable_path, options=options, log_path=log_path, firefox_options=firefox_options, service_args=service_args)
        self.dcu_wait_time = wait_time # seconds to wait for elements for
        self.dcu_sliding_time = sliding_time # seconds for popup sliding duration

    def dcu_find(self, css_sel):
        """Find an element on the page, waiting in case it has not loaded yet"""
        return WebDriverWait(self, self.dcu_wait_time).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_sel)))

    def dcu_finds(self, css_sel):
        """Find multiple elements on the page, waiting until at least one of the elements loads first"""
        return WebDriverWait(self, self.dcu_wait_time).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_sel)))

    def dcu_mainpage(self):
        """Wrapper for going to the main page of the DCU exam papers online database"""
        self.get(urls['main'])

    def dcu_wait_for_data(self, css_selector, time=30):
        """Blocks further execution until the data referenced by 'css_selector' loads, or times out"""
        WebDriverWait(self, time).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))

    #@on(urls['main'])
    def dcu_howmany(self):
        """Return a Select object of the drop down menu that allows the user to choose how many papers to display"""
        return Select(self.dcu_find(css_sels['howmany']))

    def dcu_show_max(self):
        """Show the maximum number of papers on a page"""
        select = self.dcu_howmany()
        largest_value = str(max([int(opt.get_attribute('value')) for opt in select.options]))
        select.select_by_value(largest_value)
        assert select.first_selected_option.get_attribute('value') == largest_value
        return select.first_selected_option.get_attribute('value')

    def dcu_show_min(self):
        raise NotImplementedError
        
    def dcu_show_index(self, i=0):
        raise NotImplementedError
        
    def dcu_show_value(self, v='10'):
        raise NotImplementedError

    def dcu_show_key(self, **kwargs):
        """Keyword argument: key function / value / index -> relevant choice on the show element"""
        raise NotImplementedError

    def dcu_set_module(self, module_filter='', preclear=False):
        """Enter text into the 'search module' field, filtering the papers by subject/module code,
        eg: ca208, CA117 (case-insensitive)"""
        modfilter = self.dcu_find(css_sels['modfilter'])
        if preclear:
            modfilter.clear()
        modfilter.send_keys(module_filter)

    def dcu_clear_module(self):
        """Clears the module field of any input (shows all papers). Wrapper for 'dcu_set_module'"""
        self.dcu_set_module(module_filter='', preclear=True)

    def dcu_sort(self):
        """Tuple of elements pointing to the data sorting arrows
        The tuple is (module, year, link)"""
        return self.dcu_finds(css_sels['sort_s'])

    def dcu_sort_by(self, option='', order=''):
        """Retrieve a sort element and achieve a specific sort order"""
        raise NotImplementedError

    def dcu_next_button(self):
        """Element for going to the next page in a papers list"""
        return self.dcu_find(css_sels['next'])

    def dcu_prev_button(self):
        """Element for going to the previous page of a paper list"""
        return self.dcu_find(css_sels['prev'])

    def dcu_deactivate_popup(self):
        """Agree to the sliding cookies/data notice pop-up and wait until it disappears"""
        popup_button = self.dcu_find(css_sels['popupbutton'])
        popup_button.click()
        WebDriverWait(self, self.dcu_sliding_time).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, css_sels['popupbutton'])))

    def dcu_infodatum(self):
        """Retrieve a dictionary representing parts of the infodatum that can be found at the bottom of a DCU papers webpage
        The infodatum gives information on the range of papers being displayed ('from' and 'to' keys), 
        the total number of filtered papers ('of'), and the total number of papers the database has overall ('total')"""
        info = self.dcu_find(css_sels['infodatum'])
        nums = []
        for token in info.text.split():
            try:
                token = token.replace(',', '')
                num = int(token) # ValueError if not convertible
                nums.append(num)
            except ValueError:
                continue
        names = ['from', 'to', 'of', 'total']
        info_nums = {name:num for name, num in zip(names, nums)}
        return info_nums    

    def dcu_total_pagination(self):
        """Return the number of pages of papers that the papers webpage displays, 
        using the infodatum at the bottom of the webpage"""
        datum = self.dcu_infodatum()
        entries = datum['to']-datum['from']+1
        total = datum['of']
        pages, overflow = divmod(total, entries)
        if overflow:
            pages += 1
        return pages

    def dcu_page_papers(self, func_expr='n'):
        """func_expr is an expression in the CSS selector 'nth-' Functional Notation
        eg: n gets all the papers, 2n gets all the even number papers, 
        3n+1 starts at 1 and gets all papers that are multiples of added 3's"""
        return self.dcu_finds(css_sels['paper_s'].format(func_expr))

    def dcu_all_page_papers(self):
        """Get all the papers on a single page. Wrapper for 'dcu_page_papers'"""
        return self.dcu_page_papers('n')

    def dcu_paper_link(self, paper_elem):
        """Directly get the link to a paper given an element that points to the paper"""
        return paper_elem.find_element_by_css_selector(css_sels['paper_link']).get_attribute('href')

    def dcu_paper_data(self, paper_elem):
        """Return a tuple (module, year, link) of paper data from a paper element"""
        mod, year, link = paper_elem.find_elements_by_css_selector(css_sels['paper_data_s'])
        return (mod.text, year.text, link.find_element_by_css_selector('a').get_attribute('href'))

    def dcu_all_page_links(self):
        """A list of links to each of the papers displayed on the current page"""
        return [self.dcu_paper_link(element) for element in self.dcu_all_page_papers()]

    def dcu_dlpage(self, url):
        """Wrapper for getting the download page of a paper given the paper's URL"""
        self.get(url)

    #@on_root(urls['dl_root'])
    def dcu_download(self):
        """Saves a PDF locally, using the profile preferences of the browser instance"""
        self.dcu_wait_for_data(css_sels['dldata'])
        self.dcu_find(css_sels['dlbutton']).click()

    @staticmethod
    def dcu_autosave_profile(profile_class=webdriver.FirefoxProfile):
        """Return a browser profile preferences object with suitable preferences set,
        so that downloads are done automatically and saved to the desired directory"""
        profile = profile_class()
        preferences = {
            'browser.helperApps.neverAsk.saveToDisk':'application/pdf',
            'browser.download.folderList': 2,
            'browser.download.dir': paths['save_dir'],
            'browser.downloads.useDownloadDir': True,
            'pdfjs.disabled': True,
            'browser.download.manager.useWindow': False,
            'browser.download.manager.showWhenStarting': False,
            'browser.download.manager.focusWhenStarting': False,
            'browser.donwload.manager.flashCount': 0,
            'browser.download.manager.showAlertOnComplete': False,
            'browser.download.manager.closeWhenDone': True,
        }
        for (key, value) in preferences.items():
            profile.set_preference(key, value)
        return profile


class DCU_Webscraper():
    """An instance of a web scraping session, 
    with more complex functions to interact with the DCU webpage wrapper"""

    def __init__(self, browser=None, module=''):
        if browser == None:
            browser = DCU_Website()
        self.browser = browser
        if not module:
            print('Warning. It looks like that you might be attempting to scrape the entirety of all the available papers in the database! Are you sure you are up to such a feat???!!!')
        self.module = module

    def scrape_all(self):
        self.browser.dcu_mainpage()
        self.browser.dcu_wait_for_data(css_sels['paperdata'])
        self.browser.dcu_deactivate_popup()
        self.browser.dcu_set_module(self.module)
        self.browser.dcu_show_max()

        papers = self.browser.dcu_all_page_links()
        nexts = self.browser.dcu_total_pagination()-1 
        for i in range(nexts):
            self.browser.dcu_next_button().click()
            papers += self.browser.dcu_all_page_links()

        for url in papers:
            self.browser.dcu_dlpage(url)
            self.browser.dcu_download()
        time.sleep(8)

        return papers

    def scrape_some():
        raise NotImplementedError

    def scrape_filter():
        raise NotImplementedError


## command-line interface

def main():
    args = sys.argv[1:]
    if len(args) == 2:
        module, directory = args
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        paths['save_dir'] = directory
    elif len(args) == 1:
        module = args
    else:
        raise NotEnoughArgumentsError("Need a required 'module' argument and an optional 'directory' argument")

    print('Setting up...')
    scraper = DCU_Webscraper(browser=DCU_Website(firefox_profile=DCU_Website.dcu_autosave_profile(), executable_path=paths['driver']), module=module)
    print('Scraping...')
    scraper.scrape_all()
    print('Done')
    scraper.browser.quit()

if __name__ == '__main__':
    main()