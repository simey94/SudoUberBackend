import weather_forecaster

def priceCalculation(location):
    basePrice = 1.00
    degreesC = weather_forecaster.getDegreesC(location)

    if(degreesC > 15):
        basePrice = basePrice * 1.2
    elif(degreesC > 20):
        basePrice = basePrice * 1.5

    return basePrice

