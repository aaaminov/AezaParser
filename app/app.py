from flask import Flask, render_template, request
from parser import db, Location, Server, Tariff, scrape_all_locations, create_app

app = create_app()

# для получения данных из БД с фильтрацией
def get_filtered_data(server_types, min_cores=None, min_ram=None, min_rom=None):

    query = (
        db.session.query(Tariff, Server, Location)
        .join(Server, Tariff.server_id == Server.id)
        .join(Location, Server.location_id == Location.id)
    )

    results = {}

    # из БД
    for tariff, server, location in query.all():

        if not server.server_type in server_types:
            continue

        specs = tariff.tariff_specs.split(", ")
        cores = int(specs[0].split(" ")[0])  # core
        ram = int(specs[1].split(" ")[0])  # GB RAM
        rom = int(specs[2].split(" ")[0])  # GB ROM

        # фильтры
        if min_cores and cores < min_cores:
            continue
        if min_ram and ram < min_ram:
            continue
        if min_rom and rom < min_rom:
            continue

        # Группируем данные по серверным типам
        if server.server_type not in results:
            results[server.server_type] = {}

        if location.name not in results[server.server_type]:
            results[server.server_type][location.name] = {
                "img_src": location.img_src,
                "about_server_type": server.type_specs,
                "tariffs": []
            }


        # results[server.server_type][location.name]["tariffs"].append({
        #     "tariff_name": tariff.tariff_name,
        #     "promo": tariff.promo,
        #     "price_per_hour": tariff.price_per_hour,
        #     "price_per_month": tariff.price_per_month,
        #     "order_link": tariff.order_link,
        # })
        tariff_data = {
            "tariff_name": tariff.tariff_name,
            "promo": tariff.promo,
            "first_month_price": tariff.first_month_price,
            "tariff_specs": tariff.tariff_specs,
            "price_per_hour": tariff.price_per_hour,
            "price_per_month": tariff.price_per_month,
            "order_link": tariff.order_link,
        }
        if tariff_data not in results[server.server_type][location.name]["tariffs"]:
            results[server.server_type][location.name]["tariffs"].append(tariff_data)

    return results


@app.route('/', methods=['GET'])
def index():
    server_types = request.args.getlist('server_type')  # Тип сервера (несколько)
    min_cores = request.args.get('min_cores', 0, type=int)
    min_ram = request.args.get('min_ram', 0, type=int)
    min_rom = request.args.get('min_rom', 0, type=int)

    if len(server_types) == 0:
        server_types = ['Promo', 'Shared', 'Dedicated']

    print("server_types: ")
    print(server_types)

    data = get_filtered_data(server_types, min_cores, min_ram, min_rom)

    return render_template(
        'index.html',
        server_types=server_types,
        min_cores=min_cores,
        min_ram=min_ram,
        min_rom=min_rom,
        data=data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание таблиц
        locations_data = scrape_all_locations()

        # в консоль
        if locations_data:
            for location_data in locations_data:
                print(f"Локация: {location_data['location']}")
                print(f"Изображение: {location_data['img_src']}")
                print("-" * 40)

                for server in location_data['servers']:
                    print(f"Тип сервера: {server['server_type']}")
                    print(f"Описание: {server['description']}")
                    print(f"Характеристики: {', '.join(server['type_specs'])}")
                    print("Тарифы:")
                    for tariff in server["tariffs"]:
                        print(f"  Тариф: {tariff['tariff_name']}")
                        if tariff['promo']:
                            print(f"    Метки: {', '.join(tariff['promo'])}")
                        else:
                            print("    Метки: Нет")
                        print(f"    Цена за первый месяц: {tariff['first_month_price']}")
                        print(f"    Характеристики: {', '.join(tariff['tariff_specs'])}")
                        print(f"    Цена за час: {tariff['price_per_hour']}, за месяц: {tariff['price_per_month']}")
                        print(f"    Ссылка на заказ: {tariff['order_link']}")
                    print("-" * 40)
                print("=" * 40)

    app.run(host='0.0.0.0', port=7777, debug=True)