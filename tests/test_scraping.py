import pytest
import json
from PIL import Image
from scuts.scraping import download_img, CustomDriver
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# def test_download_img():
#     img_prefix_path = '/tmp/img'
#     print(img_prefix_path)
#     url = 'https://docs.pytest.org/en/2.8.7/_static/pytest1.png'
#     img_path = download_img(url, img_prefix_path)
#     with Image.open(img_path) as img_f:
#         assert img_f.size == (150, 143)
#
#     hard_img_url1 = "http://www2.takashimaya.co.jp/sto/image/product/product_image_main/0576/0000880576-001a.jpg"
#     hard_img_url2 = "https://www.davidjones.com/productimages/medium/1/1842107_15119019_1220114.jpg"
#     hard_img_url3 = "https://www.bottleworld.de/media/catalog/product/cache/1/image/650x650/9df78eab33525d08d6e5fb8d27136e95/6/5/6552_newton_redlabel_chardonnay.jpg"
#     hard_img_url4 = "https://specsonline.com/wp-content/uploads/2018/11/008175381624-2.jpg"
#     hard_img_url5 = "https://target.scene7.com/is/image/Target/GUEST_1f1708b8-a5e2-44a2-926e-e0f42db67d36?wid=488&hei=488&fmt=webp"
#     hard_img_url6 = "https://www.31dover.com/media/catalog/product/cache/1/image/1000x1000/85e4522595efc69f496374d01ef2bf13/p/r/product_31d5340_veuvecliquotgouacherose.jpg"
#
#     images_urls = [hard_img_url1, hard_img_url2, hard_img_url3, hard_img_url4, hard_img_url5, hard_img_url6]
#     for ix, image_url in enumerate(images_urls):
#         orig_img_path = '/tmp/test_img{}.png'.format(ix)
#         img_path = download_img(image_url, orig_img_path, shop_id="test", decode_content=False, debug=True)
#         with Image.open(img_path) as img_f:
#             assert img_f.size[0] > 10
#             assert img_f.size[1] > 10
#
#
# def test_anonymity():
#     driver = CustomDriver(firefox=True, timeout=20)
#     anonymous_ip = json.loads(driver.get_with_proxy('https://api.ipify.org?format=json').driver.find_element_by_id("json").text)['ip']
#     driver = CustomDriver(firefox=True, timeout=20)
#     normal_ip = json.loads(driver.get('https://api.ipify.org?format=json').driver.find_element_by_id("json").text)['ip']
#     print(normal_ip, anonymous_ip)
#     assert normal_ip != anonymous_ip
