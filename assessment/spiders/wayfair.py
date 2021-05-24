import scrapy
from urllib.parse import urljoin
class WayfairSpider(scrapy.Spider):
    name = 'wayfair'
    start_urls = 'https://www.wayfair.com/kitchen-tabletop/sb0/coffee-makers-c419252.html'
    def start_requests(self):
        yield scrapy.Request(self.start_urls, callback=self.parse, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'})

    def parse(self, response):
        products = response.xpath("//*[contains(@class, 'ProductCard-container')]/a/@href").extract()
        for p in products:
            url = urljoin(response.url, p)
            yield scrapy.Request(url, callback=self.parse_product,headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'})
        
        pagination_links = response.xpath("//*[contains(@class, 'pl-Pagination-icon--next')]/a/@href")
        yield response.follow_all(pagination_links, self.parse,headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'})
    
    def parse_product(self, response):
       for info in response.xpath("//*[contains(@class, 'ProductDetailInfoBlock-header')]"):
            yield {
                'categories': info.xpath("//li[has-class('Breadcrumbs-listItem')]/a//text()").extract(),
                'sku': info.xpath("//span[has-class('Breadcrumbs-item')]/text()").re_first(r'SKU:\s*(.*)'),
                'part_no': info.xpath("//span[has-class('Breadcrumbs-item')]/text()").re_first(r'Part #:\s*(.*)'),
                'image_url': info.xpath("//img[has-class('pl-FluidImage-image')]/@src").extract_first(),
                'product_name': info.xpath("//h1[has-class('pl-Heading')]/text()").extract_first(),
                'brand': info.xpath("//p[has-class('ProductDetailInfoBlock-header-manu')]/a//text()").extract_first(),
                'rating': info.xpath("//span[has-class('ProductRatingNumberWithCount-rating')]//text()").extract_first(),
                'reviews': info.xpath("//span[has-class('ProductRatingNumberWithCount-count--link')]//text()").re_first(r'^[0-9]*$'),
                'price': info.xpath("//div[has-class('BasePriceBlock')]/span[has-class('notranslate')]//text()").extract_first(),
                'overview': info.xpath("//span[has-class('VisualizationContentIllustratedInfo-description')]//text()").extract(),
                'description': info.xpath("//div[has-class('ProductOverviewInformation-content')]//text()").extract_first(),
            }