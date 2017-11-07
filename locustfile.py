from locust import HttpLocust, TaskSet, task
from http.cookies import SimpleCookie
from bs4 import BeautifulSoup
import json

HOST = "http://localhost:8000"
MIN_WAIT = 5000
MAX_WAIT = 9000

class Helpers:
    def parse_csrf(self, string):
        tag = BeautifulSoup(string, "html.parser").find("input", attrs={"name":"csrfmiddlewaretoken"})
        if tag is not None:
            return tag["value"]

    def post_ajax(self, url, params):
        csrf_token = self.client.cookies.get("csrftoken", "")
        response =  self.client.post(url, params, headers={"X-CSRFToken": csrf_token, "X-Requested-With": "XMLHttpRequest"})
        #These ajax responses don't have domains in the cookie so CookieJar is throwing them away
        self.store_cookies(response)
        return response

    def store_cookies(self, response):
        cookies = SimpleCookie(response.headers["Set-Cookie"])
        for key, item in cookies.items():
            self.client.cookies.set(item.key, item.value)

    def parse_product_links(self, string):
        links = BeautifulSoup(string, "html.parser").select(".category-list a")
        return [ link['href'] for link in links ]

    def parse_variants(self, string):
        soup = BeautifulSoup(string, "html.parser")
        variants = soup.select_one("#variant-picker")["data-variant-picker-data"]
        return json.loads(variants)["variants"]

class VisitorBehavior(TaskSet, Helpers):
    @task(100)
    def buy(self):
        self.client.get("/")
        response = self.client.get("/products/category/apparel-1/")
        first_product = self.parse_product_links(response.text)[0]
        response = self.client.get(first_product)
        first_variant = self.parse_variants(response.text)[0]["id"]
        response = self.post_ajax("{0}add/".format(first_product), {"quantity":1, "variant":first_variant })
        response = self.client.get("/checkout/")
        csrf_token = self.parse_csrf(response.text)
        response = self.client.post("/checkout/shipping-address/", {
            "csrfmiddlewaretoken":csrf_token,
            "email":"test@example.com",
            "phone":"1234567890",
            "first_name": "Joe",
            "last_name": "Doe",
            "company_name": "",
            "street_address_1": "123 Main St",
            "street_address_2": "",
            "city": "The Land",
            "country_area": "OH",
            "postal_code": "44111",
            "country": "US",
        })
        csrf_token = self.parse_csrf(response.text)
        response = self.client.post("/checkout/shipping-method/", {
            "csrfmiddlewaretoken":csrf_token,
            "method": "1"
        })
        csrf_token = self.parse_csrf(response.text)
        response = self.client.post("/checkout/summary/", {
            "csrfmiddlewaretoken":csrf_token,
            "address": "shipping_address"
        })
        csrf_token = self.parse_csrf(response.text)
        response = self.client.post(response.url, {
            "csrfmiddlewaretoken":csrf_token,
            "method": "default"
        }, name="/order/[order-id]/payment")

class Visitor(HttpLocust):
    weight = 5
    task_set = VisitorBehavior
    host = HOST
    min_wait = MIN_WAIT
    max_wait = MAX_WAIT
