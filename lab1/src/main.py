from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from lxml import etree
import os
import webbrowser


def cleanup():
    try:
        os.remove("task1.xml")
        os.remove("task2.xml")
        os.remove("task2.xhtml")
    except OSError:
        pass


def scrap_data():
    process = CrawlerProcess(get_project_settings())
    process.crawl('books')
    process.crawl('hozmart')
    process.start()


def task1():
    print("Task #1")
    root = etree.parse("task1.xml")
    count = root.xpath("count(//page/fragment[@type='text']) div count(//page)")
    print("Avarage number of text fragments: %d" % (count))


def task2():
    print("Task #2")
    transform = etree.XSLT(etree.parse("task2.xsl"))
    result = transform(etree.parse("task2.xml"))
    result.write("task2.xhtml", pretty_print=True, encoding="UTF-8")
    print("XHTML page will be opened in web-browser...")
    webbrowser.open('file://' + os.path.realpath("task2.xhtml"))


if __name__ == '__main__':
    print("Lab #1")
    print("Cleanup files...")
    cleanup()
    print("done")
    print("Scrapping data from sites...")
    scrap_data()
    print("finished")
    while True:
        print("-" * 45)
        print("Input number of task to execute, or something else to exit:")
        print("1. Task #1")
        print("2. Task #2")
        print("> ")
        number = input()
        if number == "1":
            task1()
        elif number == "2":
            task2()
        else:
            break
    print("Exiting...")

    
