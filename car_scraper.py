'''scrape used car data of common car makes from cars.com'''
from requests import get
from bs4 import BeautifulSoup

__author__ = 'Jacob Hajjar'
__email__ = 'hajjarj@csu.fullerton.edu'
__maintainer__ = 'jacobhajjar'

def scrape_car_page(make, model_list, car_tag):
    '''scrape the data from the car's page from tag and populate the dict to be returned'''
    car_url = "https://www.cars.com" + car_tag.get('href')
    response = get(car_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    #create dict to define the order and properties of a car
    car = {'year': None, 'make': None, 'model': None, 'exterior_color': None, 'interior_color': None, 'drivetrain': None, 
        'fuel_type': None, 'transmission': None, 'milage': None, 'accidents': None, '1_owner': None, 'personal_used': None}
    #get the car title as a list of each word
    car_title = soup.find('h1', class_ = 'listing-title').string.split()
    #get and validate the year from the car title
    try:
        year = int(car_title[0])
        if year > 1950 and year <= 2023:
            car['year'] = year
            car_title.pop(0)
        else:
            return
    except:
        print("error getting the year")
        return
    #get make by matching the make inside the title
    make_list = make.split()
    if all(_ in car_title for _ in make_list):
        car['make'] = make
        del car_title[:len(make_list)]
    else:
        print("make not found in title")
        return
    print(car_title)
    #get the model by matching the longest model in the title
    matched_car_models = []
    for model in model_list:
        if all(x in car_title for x in model):
            ''''''

def scrape_car_make(make):
    '''scrape the car data of the current make'''
    url = 'https://www.cars.com/shopping/results/'
    cars_per_page = 100
    car_type = {'page_size': cars_per_page, 'stock_type': 'used', 'makes': make.replace(" ", "_"), 'zip': '92801'}
    response = get(url, params=car_type)
    soup = BeautifulSoup(response.content, 'html.parser')
    #f = open("page.html", "a")
    #f.write(str(response.content))
    #f.close()

    #find the section containing text of the current models
    models = soup.find(string = make + " models")
    #get the parent tag and search it to find a list of the tags of the models being sold
    model_tag_list = models.parent.parent.find_all('label', class_ = 'sds-label')
    model_list = []
    for model_tag in model_tag_list:
        #for each model tag, get the model's name as text with no whitespace
        model_text = model_tag.find(text=True, recursive=False).strip()
        if model_text not in model_list:
            model_list.append(model_text)
    print(model_list)
    #get the number of listings
    listings = soup.find('span', class_= 'total-filter-count')
    print(listings.string)
    #get number of pages 
    #scrape all the cars on the page
    car_tag_list = soup.find_all('a', class_=
                                 'image-gallery-link vehicle-card-visited-tracking-link')
    for car_tag in car_tag_list:
        scrape_car_page(make, model_list, car_tag)



def get_cars_data(file):
    '''get the various car attributes from the given url and append it to the file'''
    #TODO get the list of popular makes from cars.com
    current_make = 'Land Rover'
    scrape_car_make(current_make)

def main():
    '''the main function'''

    #url = 'https://www.cars.com/shopping/results/?dealer_id=&keyword=&list_price_max=70000&list_price_min=&makes[]=&maximum_distance=all&mileage_max=&page_size=20&sort=best_match_desc&stock_type=used&year_max=&year_min=&zip=92801'

    get_cars_data('used_cars.csv')

if __name__ == '__main__':
    main()
