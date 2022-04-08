#!/usr/bin/env python

from urllib2        import urlopen
from BeautifulSoup  import BeautifulSoup
from lxml           import etree
import re, csv, code

city_list             = open("/Users/vert/Downloads/Web Scrap/reredditscrapingjob/city_names_sp.txt", "r").read().splitlines(',')


base_url              = "http://www.sobracil-sp.org.br/novo/pesquisamedicos/index.php?RadioGroup1=cidade&nome={0}&pesquisar=Pesquisar"
domain_url            = "http://www.sobracil-sp.org.br/novo/pesquisamedicos/"
person_links_xpath    = "//img[@src='btn_info.gif']/../@href"
person_details_xpath  = "//td[@valign='top']/p"
email_xpath           = "//td[@valign='top']/p/a/text()"
tel_regex             = 'Tel.: ([(.|\-)0-9]+) -'

with open('details.csv', 'wb') as csvfile:
  writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
  writer.writerow(['Name', 'Speciality', 'Address', 'Phone', 'Email', 'City'])
  for city in city_list:
    print "In city {0}".format(city)
    response      = urlopen(base_url.format(city))
    htmlparser    = etree.HTMLParser()
    results_tree  = etree.parse(response, htmlparser)
    links         = results_tree.xpath(person_links_xpath)

    # List of cities that does not contain any results
    open("cities_with_missing_details.txt", "a").write(city + "\n") if len(links) <= 0 else None

    # Loop through all the links of the people
    for link in links:
      url           = domain_url + link
      response      = urlopen(url)
      htmlparser    = etree.HTMLParser()
      details_tree  = etree.parse(response, htmlparser)
      details       = details_tree.xpath(person_details_xpath)

      # Get the text from the nodes
      details       = map(lambda x: x.text, details)
      # Eliminate all empty lines
      details       = [detail for detail in details if detail is not None]
      # Extract the email separately
      email         = details_tree.xpath(email_xpath)[0]

      name = details[0].split('-')[0:-1]
      name = name[0].strip() if len(name) > 0 else None

      speciality    = details[0].split('-')[-1].strip()
      address       = ' '.join(details[1:-1]).strip()
      tel           = ''.join([y for y in details[-1].split("Tel")[-1].split("E-mail")[0].strip() if y.isdigit() or y == ' ']).strip()

      # Coerce into Ascii
      row           = [ x.encode('ascii', errors='ignore') if x is not None else None for x in [name, speciality, address, tel, email, city] ]

      # Write the details
      writer.writerow(row)
