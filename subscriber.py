from pysimplesoap.client import SoapClient
# Create SOAP client
client = SoapClient(
    location='http://localhost:8888/',
    action='http://localhost:8888/',  # SOAPAction
    soap_ns='soap',
    trace=False,
    ns=False)