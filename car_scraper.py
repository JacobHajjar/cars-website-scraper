'''scrape used car data of common car makes from cars.com'''
from math import ceil
from re import sub
from csv import writer
from requests import get, exceptions
from bs4 import BeautifulSoup

__author__ = 'Jacob Hajjar'
__email__ = 'jacob.hajjar1@gmail.com'
__maintainer__ = 'jacobhajjar'


def get_car_attribute(soup, attribute_name):
    '''using the attribute name, search for the attribute and return
    its value if successfully found or none'''
    attribute_term_tag = soup.find('dt', string=attribute_name)
    if attribute_term_tag:
        attribute_data = str(
            attribute_term_tag.nextSibling.next_sibling.string).strip()
        if len(attribute_data) > 1:
            if attribute_name == 'Mileage':
                try:
                    attribute_data = sub(
                        '[^0-9]', '', attribute_data.split()[0])
                except ValueError:
                    print("failed to get mileage")
                    attribute_data = None
            elif attribute_name == "Accidents or damage":
                if attribute_data == 'None reported':
                    attribute_data = False
                elif attribute_data == 'At least 1 accident or damage reported':
                    attribute_data = True
                else:
                    print("failed to get accident report")
                    attribute_data = None
            elif attribute_name in ('1-owner vehicle', 'Personal use only'):
                if attribute_data == "No":
                    attribute_data = False
                elif attribute_data == "Yes":
                    attribute_data = True
                else:
                    attribute_data = None
            return attribute_data
        return None
    print(attribute_name + ' was not found')
    return None


def scrape_car_page(make, model_list, car_tag):
    '''scrape the data from the car's page from tag and populate the dict to be returned,
    or return none if any of the values could not be populated'''
    car_url = "https://www.cars.com" + car_tag.get('href')
    print(car_url)
    response = get(car_url)
    try:
        response = get(car_url)
    except exceptions.ConnectionError:  # This is the correct syntax
        print("could not get car page")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    # create dict to define the order and properties of a car
    car = {'year': None, 'make': None, 'model': None, 'trim': None, 'exterior_color': None,
           'interior_color': None, 'drivetrain': None, 'fuel_type': None, 'transmission': None,
           'mileage': None, 'in_accident': None, '1_owner': None, 'personal_used': None, 'price': None}
    # get the car title as a list of each word

    # get and validate the year from the car title
    try:
        car_title = soup.find('h1', class_='listing-title').string.split()
        year = int(car_title[0])
        if 1950 < year < 2023:
            car['year'] = year
            car_title.pop(0)
        else:
            return None
    except (ValueError, AttributeError) as error:
        if error == ValueError:
            print("invalid year retrieved")
        else:
            print("could not retrieve title")
        return None
    # get make by matching the make inside the title
    make_list = make.split()
    if all(_ in car_title for _ in make_list):
        car['make'] = make
        del car_title[:len(make_list)]
    else:
        print("make not found in title")
        return None
    # get the model by matching the longest model in the title
    matched_car_models = []
    for model in model_list:
        if all(_ in car_title for _ in model.split()):
            matched_car_models.append(model)
    if len(matched_car_models) > 0:
        car_model = max(matched_car_models, key=len)
        car['model'] = car_model
        del car_title[:len(car_model.split())]
    else:
        return None
    # get the car's trim from the remaining words in the title
    car['trim'] = ' '.join(car_title)
    # get the exterior color
    car['exterior_color'] = get_car_attribute(soup, 'Exterior color')
    # get the interior color
    car['interior_color'] = get_car_attribute(soup, 'Interior color')
    # get the drivetrain
    car['drivetrain'] = get_car_attribute(soup, 'Drivetrain')
    # get the fuel type
    car['fuel_type'] = get_car_attribute(soup, 'Fuel type')
    # get the transmission type
    car['transmission'] = get_car_attribute(soup, 'Transmission')
    # get the milage
    car['mileage'] = get_car_attribute(soup, 'Mileage')
    # get if it was in an accident
    car['in_accident'] = get_car_attribute(soup, 'Accidents or damage')
    # get if the car had 1 owner
    car['1_owner'] = get_car_attribute(soup, '1-owner vehicle')
    # get if the car was personally used or not (business used)
    car['personal_used'] = get_car_attribute(soup, 'Personal use only')
    # lastly get the price TODO
    price_string = soup.find(
        'header', class_='gallery-header').find('span', class_='primary-price').string
    try:
        car['price'] = int(sub('[^0-9]', '', price_string))
    except ValueError:
        print("price could not be initialized")
    if None in car.values():
        print("car not initialized with all attributes")
        return None
    print(car)
    return car.values()


def scrape_car_make_page(make, model_list, file_name, soup):
    '''scrape a single page of the car make'''
    car_tag_list = soup.find_all(
        'a', class_='image-gallery-link vehicle-card-visited-tracking-link')
    with open(file_name, 'a', newline='', encoding="utf-8") as file:
        data_writer = writer(file)
        number_of_car = 1
        for car_tag in car_tag_list:
            number_of_car += 1
            car_data = scrape_car_page(make, model_list, car_tag)
            if car_data:
                data_writer.writerow(car_data)
            else:
                continue


def scrape_car_make(make, file_name):
    '''scrape the car data of the current make from all pages'''
    url = 'https://www.cars.com/shopping/results/'
    cars_per_page = 100
    page_parameters = {'page': 1, 'page_size': cars_per_page, 'stock_type': 'used',
                       'makes': make.replace(" ", "_"), 'zip': '92801'}
    response = get(url, params=page_parameters)
    soup = BeautifulSoup(response.content, 'html.parser')

    # find the section containing text of the current models
    models = soup.find(string=make + " models")
    # get the parent tag and search it to find a list of the tags of the models being sold
    model_tag_list = models.parent.parent.find_all('label', class_='sds-label')
    model_list = []
    for model_tag in model_tag_list:
        # for each model tag, get the model's name as text with no whitespace
        model_text = model_tag.find(text=True, recursive=False).strip()
        if model_text not in model_list:
            model_list.append(model_text)
    print(model_list)
    # get the number of listings and calculate the pages
    listings_string = soup.find(
        'span', class_='total-filter-count').string.split()[0]
    print(listings_string)
    num_pages = 0
    try:
        num_listings = int(sub('[^0-9]', '', listings_string))
        num_pages = ceil(num_listings / cars_per_page)
        print(num_pages)
    except ValueError:
        print("could not get number of listings for " + make)
        return
    # scrape all the cars on the page
    scrape_car_make_page(make, model_list, file_name, soup)
    for page_num in range(2, num_pages + 1):
        page_parameters['page'] = page_num
        print("scraping page " + str(page_num))
        response = get(url, params=page_parameters)
        soup = BeautifulSoup(response.content, 'html.parser')
        scrape_car_make_page(make, model_list, file_name, soup)


def get_cars_data(file_name):
    '''get the various car attributes from the given url and append it to the file'''
    url = 'https://www.cars.com/'
    response = get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    popular_makes_tag = soup.find('optgroup', label='Popular makes').find_all('option')
    for popular_make_tag in popular_makes_tag:
        scrape_car_make(popular_make_tag.string, file_name)


def main():
    '''the main function'''
    get_cars_data('used_cars.csv')


if __name__ == '__main__':
    main()
