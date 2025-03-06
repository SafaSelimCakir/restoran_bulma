import re

def verify_phone_number(phone):
    """ Telefon numarasının geçerli olup olmadığını kontrol eder. """
    phone_pattern = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    return bool(phone_pattern.match(phone))

def verify_restaurant_name(name):
    """ Restoran isminin mantıklı olup olmadığını kontrol eder. """
    common_words = ["Restoran", "Cafe", "Lokanta", "Kebap", "Pide", "Bar", "Bistro"]
    return any(word in name for word in common_words)

def verify_data(restaurants):
    """ Restoran listesini doğrular. """
    verified_list = []
    for rest in restaurants:
        if verify_phone_number(rest["phone"]) and verify_restaurant_name(rest["name"]):
            verified_list.append(rest)

    return verified_list
