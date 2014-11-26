from scrapy import log
from scrapy.spider import Spider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request

from pricecrawl.xpaths import *

from price_display.models import price_display
"""
The spider responsible for crawling amazon.in
"""
class AmazonSpider(Spider):
  name = 'amazon'
  allowed_domains = ['amazon.in']
  start_urls = []
  item_name = ""
  """
    Initialises the start_urls based upon the input dates.
  """
  def __init__(self, *args, **kwargs):
    try:
      tup = kwargs.get('product').split()
      product_name = tup[0]
      for i in xrange(1,len(tup)):
	product_name+='+'+tup[i]
      self.item_name = product_name
      self.start_urls.append(START_URL_PREFIX_az + product_name)
    except Exception as e:
      print e

  """
    The main parser for getting responses from the list of
    start_urls.
  """
  def parse(self, response):
    hxs = HtmlXPathSelector(response)
    pid = hxs.select(PRODUCT_ID_az).extract()
    first_product = pid[0]
    url = BASE_URL_az+'gp/offer-listing/'+first_product
    yield Request(url,self.get_details)

  def get_details(self,response):
    hxs = HtmlXPathSelector(response)
    pages = hxs.select(PAGE_NAVIGATOR_az).extract()
    products = hxs.select(PRODUCT_NAME_az).extract()
    first_product_name = products[4]
    prices = hxs.select(PRODUCT_SELLER_PRICES_az).extract()
    sellers = hxs.select(PRODUCT_SELLER_NAMES_az).extract()
    sellers_2 = hxs.select(PRODUCT_SELLER_NAMES_az_2).extract()
    #print sellers
    cnt = 0
    for i in xrange(0,len(prices)):  
      seller = sellers[i].split('"')
      for j in xrange(0, len(seller)):
	if 'alt' in seller[j]:
	  #print "found"
	  sellers[i] = seller[j+1]
	  break
      else:
	sellers[i] = sellers_2[cnt]
	cnt += 1
      s = price_display(product_name = first_product_name, sellername = sellers[i], portalname="amazon", itemname=self.item_name, price=prices[i])
      s.save()
    for i in xrange(1,len(pages)-1):
      url = BASE_URL_az + pages[i]
      yield Request(url, self.store_pages)

  def store_pages(self,response):
    hxs = HtmlXPathSelector(response)
    products = hxs.select(PRODUCT_NAME_az).extract()
    first_product_name = products[4]
    prices = hxs.select(PRODUCT_SELLER_PRICES_az).extract()
    sellers = hxs.select(PRODUCT_SELLER_NAMES_az).extract()
    sellers_2 = hxs.select(PRODUCT_SELLER_NAMES_az_2).extract()
    cnt = 0
    for i in xrange(0,len(prices)):
      seller = sellers[i].split('"')
      for j in xrange(0, len(seller)):
	if 'alt' in seller[j]:
	  #print "found"
	  sellers[i] = seller[j+1]
	  break
      else:
	sellers[i] = sellers_2[cnt]
	cnt += 1
      s = price_display(product_name = first_product_name, sellername = sellers[i], portalname="amazon", itemname=self.item_name, price=prices[i])
      s.save()