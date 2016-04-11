import weather_forecaster


def price_calculation(location):
    journeyPrice = 1.00
    degreesC = weather_forecaster.get_degrees_c(location)

    if degreesC > 15:
        journeyPrice *= 1.2
    elif degreesC > 20:
        journeyPrice *= 1.5

    return journeyPrice