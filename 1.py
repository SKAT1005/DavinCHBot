from dadata import Dadata


token = "4583e64a2cb38b80687b30677ceacd1354c39118"
secret = "9bf0c719aacb21dcdc38614b4f2e803f645f5317"
dadata = Dadata(token, secret)
result = dadata.clean("address", "Бульвар менделеева 16")
print(result)
print(result['qc_geo'])
print(result['settlement'])
print(result['city'])