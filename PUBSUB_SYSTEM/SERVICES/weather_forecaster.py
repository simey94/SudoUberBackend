import sys
sys.path.append("../..")

from pywwo import *
def get_degrees_c(location):
    setKey('<45a7v53q9qaveabsekth9ucc>', 'free')
    w = LocalWeather(location)
    # print w.data.current_condition.temp_C
    return w.data.current_condition.temp_C