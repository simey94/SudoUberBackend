import holidays
import weather_forecaster
import timing_service


def price_calculation(demand, supply, location):
    journeyPrice = 1.00  # £1 per mile

    # Get pricing formulae components from other services
    degreesC = weather_forecaster.get_degrees_c(location)
    currentDateTime = timing_service.timing_pricing()
    us_holidays = holidays.UnitedStates()  # package is lame and doesn't do UK

    if currentDateTime.date() in us_holidays:
        journeyPrice *= 1.2
    if demand > supply:
        journeyPrice *= 1.2
    if degreesC > 15:
        journeyPrice *= 1.2
    elif degreesC > 20:
        journeyPrice *= 1.5

    return journeyPrice