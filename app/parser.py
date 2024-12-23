import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///locations_data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

# Модели БД
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    img_src = db.Column(db.String(200), nullable=False)
    servers = db.relationship('Server', backref='location', lazy=True)

class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    type_specs = db.Column(db.String(300), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    tariffs = db.relationship('Tariff', backref='server', lazy=True)

class Tariff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tariff_name = db.Column(db.String(100), nullable=False)
    promo = db.Column(db.String(200))  # Метки акций (если есть)
    first_month_price = db.Column(db.String(50), nullable=False)
    price_per_hour = db.Column(db.String(50))
    price_per_month = db.Column(db.String(50))
    order_link = db.Column(db.String(200), nullable=False)
    tariff_specs = db.Column(db.String(500))
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)



def scrape_all_locations():
    if Location.query.first():
        print("Парсинг не нужен, данные уже есть")
        return
    # db.session.query(Tariff).delete()
    # db.session.query(Server).delete()
    # db.session.query(Location).delete()
    # db.session.commit()

    url = 'https://aeza.net/ru/virtual-servers'

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Без GUI
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 0)

        # кнопки для переключения локаций
        location_buttons = driver.find_elements(By.CSS_SELECTOR, "button.sc-1vf1iwx-1")
        locations_data = []

        # location_id = 0
        for button in location_buttons:
            # location_id += 1
            location_name = button.find_element(By.CSS_SELECTOR, "span").text.strip()
            img_src  = button.find_element(By.TAG_NAME, "img").get_attribute("src")

            # # print(f"ID: {location_id}")
            # print(f"Локация: {location_name}")
            # print(f"Изображение: {img_src}")
            # print("-" * 40)

            # db.session.add(Location(
            #     id=location_id,
            #     name=location_name,
            #     img_src=img_src
            # ))
            # db.session.commit()

            # button.click()
            driver.execute_script("arguments[0].click();", button)

            # когда контент обновится
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-1ywz7pu-0")))

            server_data = scrape_location_data(driver)
            locations_data.append({
                "location": location_name,
                "img_src": img_src ,
                "servers": server_data,
            })

        # заполнение БД
        for location in locations_data:

            locat = Location(name=location['location'], img_src=location['img_src'])
            db.session.add(locat)
            db.session.commit()

            for server_data in location['servers']:
                server = Server(
                    server_type=server_data['server_type'],
                    description=server_data['description'],
                    type_specs=', '.join(server_data['type_specs']),
                    location_id=locat.id
                )
                db.session.add(server)
                db.session.commit()

                for tariff in server_data['tariffs']:
                    tariff_record = Tariff(
                        tariff_name=tariff['tariff_name'],
                        promo=', '.join(tariff['promo']),
                        first_month_price=tariff['first_month_price'],
                        price_per_hour=tariff['price_per_hour'],
                        price_per_month=tariff['price_per_month'],
                        order_link=tariff['order_link'],
                        tariff_specs=', '.join(tariff['tariff_specs']),
                        server_id=server.id
                    )
                    db.session.add(tariff_record)

                db.session.commit()

        return locations_data

    finally:
        driver.quit()

def scrape_location_data(driver):
    # все контейнеры для типов серверов
    containers = driver.find_elements(By.CSS_SELECTOR, "div.sc-1ywz7pu-0.ehUsYp")
    server_data = []

    # server_id = 0
    for container in containers:
        # server_id += 1
        server_type = container.find_element(By.CSS_SELECTOR, "h3.sc-1ywz7pu-2").text.strip()
        description = container.find_element(By.CSS_SELECTOR, ".sc-1ywz7pu-8 p").text.strip()
        type_specs = [
            spec.text.replace(" (?)", "").strip()
            for spec in container.find_elements(By.CSS_SELECTOR, "ul.sc-1ywz7pu-3 li")
        ]

        # db.session.add(Server(
        #     id=server_id,
        #     name=server_type,
        #     description=description,
        #     location_id=location_id
        # ))
        # db.session.commit()

        # тарифы
        tariffs = []
        tariff_elements = container.find_elements("css selector", "div.sc-8z95jh-0")

        server_id = 0
        for tariff in tariff_elements:
            # название тарифа
            tariff_name = tariff.find_element("css selector", "p.sc-8z95jh-1").text.strip()
            tariff_name = re.split(r'(<span|[\(])', tariff_name)[0].strip()

            # акция (если есть)
            promo_elements = tariff.find_elements("css selector", "span.sc-8z95jh-4")
            promos = [promo.text.strip() for promo in promo_elements] if promo_elements else []

            # описание акции (если есть)
            first_month_price_elements = tariff.find_elements("css selector", "p.sc-8z95jh-2")
            first_month_price = first_month_price_elements[0].text.strip() if first_month_price_elements else ""

            # характеристики
            tariff_specs = [
                spec.text.strip()
                for spec in tariff.find_elements("css selector", "ul.sc-8z95jh-7 li")
            ]

            price_per_hour = ""
            price_per_month = ""
            order_link = ""

            # Цены и ссылки
            price_links = tariff.find_elements("css selector", "div.sc-8z95jh-10 a")
            if len(price_links) == 1:
                # Только одна кнопка — это цена за месяц
                # price_per_hour = "N/A"
                price_per_month = price_links[0].text.replace("\n", " ").strip()
                order_link = price_links[0].get_attribute("href")
            elif len(price_links) == 2:
                # Две кнопки: первая — за час, вторая — за месяц
                price_per_hour = price_links[0].text.replace("\n", " ").strip()
                price_per_month = price_links[1].text.replace("\n", " ").strip()
                order_link = price_links[1].get_attribute("href")
            # else:
            #     # Кнопок нет
            #     price_per_hour = "N/A"
            #     price_per_month = "N/A"
            #     order_link = "N/A"

            # db.session.add(Tariff(
            #     id=server_id,
            #     name=server_type,
            #     description=description,
            #     location_id=location_id
            # ))
            # db.session.commit()

            tariffs.append({
                "tariff_name": tariff_name,
                "promo": promos,
                "first_month_price": first_month_price,
                "tariff_specs": tariff_specs,
                "price_per_hour": price_per_hour,
                "price_per_month": price_per_month,
                "order_link": order_link,
            })

        server_data.append({
            "server_type": server_type,
            "description": description,
            "type_specs": type_specs,
            "tariffs": tariffs,
        })
    return server_data



