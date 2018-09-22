# exam-tk
Exam ToolKit - a set of helper/automation programs relating to academic exams, from the perspective of the student

* *Currently this is specifically for one particular educational institution/university (Dublin City University / DCU)*
* *This is also Windows OS centric*

# Docs
Link to Google Doc resources:
* https://docs.google.com/document/d/15ldYdgrahA14a9Is9KdOaR0SoWZbnpGvs34_zI2cIhM/edit?usp=sharing
* https://docs.google.com/document/d/1dzC7RKmAv655VwB1xuNvd9XKNRlqIWvjQdUWho8wyD4/edit?usp=sharing
* https://docs.google.com/document/d/15H89yhlU96VQ6ApPe6Q9yk37P0BYNvXdZD6YYMIxXUA/edit?usp=sharing
* (**TO-DO: Proper readthedocs, etc documentation**)

## Installation/requirements/dependencies

* Python 3.7
* Python selenium library
  * ```pip install selenium```
* Firefox geckodriver
  * https://github.com/mozilla/geckodriver/releases
  * (included as .exe files in ```tools/```)

## Videos
...

## Before running the examples
```
cd <project-directory>
cd src
```

## webscraper.py
* Saves exam papers (PDF documents) onto the local computer from an online university exam papers database accessible through a URL, eg: https://www.dcu.ie/registry/past-exam-papers.shtml/
* Capable of selecting specific 'subjects' via 'module codes', filtering the list of papers. 
* Can save the entire list of papers
* The directory where the files are to be saved can be picked. Paths can be relative or absolute.

### Using the script from the command-line
```
py -3.7 webscraper.py <module_code> <directory_where_to_save>
```
eg:
```
py -3.7 webscraper.py ca117 ./../../my-exams/ca117/
```
**The script needs to be run from the src/ directory in order for the geckodriver to be found**

### API
```webscraper``` global variables for paths, URLs, CSS selectors, etc.
**TO-DO: Proper getters and setters for the globals**

```webscraper.DCU_Website``` class, a wrapper around selenium methods that interact with the DCU web page
```webscraper.DCU_Webscraper``` class, similar to above but more 'high level'

## slicer.py
* Takes in a number of PDF documents and retrieves a specific page from all the documents. The retrieved pages are added to a new single PDF file.
* For example, the exam papers '2018.pdf', '2017.pdf', and '2016.pdf' contain questions from the corresponding year's exam. At page 2, each paper has question 2 and question 3 of the year (roughly speaking). By 'slicing' these three PDF's at page 2, a new PDF is created containing question 2's and question 3's from each of the years on a single page.
* Directories containing the PDF's to be sliced can be passed to the script

### Using the script from the command-line
```
py -3.7 slicer.py <directory_from_which_to_take_pdfs> <page_to_slice_at> <directory_and_file_where_to_save>
```
eg
```
py -3.7 slicer.py ./../../my-exams/ca117/ 2 ./../../my-exams/ca117/qs3and4.pdf
```
**Page numbers are zero-based, eg: 0 is page 1, 1 is page 2, 2 is page 3, etc**

##  Tests
slicer_tests.py
**(INCOMPLETE) TO-DO: Include more tests, improve current ones***

## Known issues, TO-DO's
* Fix webdriver paths so that scripts can be run from anywhere, not just src/
* slicer.py: 'NumberObject is not subscriptable error', 'PdfReadWarning', 'x-ref tables warning'
  * check if the supplied papers are not corrupt, experiment with trying to leave out some of the papers
  * some errors skip some PDF's, some don't have an effect on the final output, some crash the program
* when Firefox automated browser automatically updataes, it and webscraper.py lose 'connection' to each other
* ...
