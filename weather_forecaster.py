from pywwo import *
setKey('<45a7v53q9qaveabsekth9ucc>', 'free')
w=LocalWeather('London')
print w.data.current_condition.temp_C