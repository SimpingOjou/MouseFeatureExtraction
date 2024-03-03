import DataManagement as Data

try:
    td_sideview = Data.TrackingData(data_name="Side view")
except Exception as e:
    print(e)
    raise

try:
    td_ventralview = Data.TrackingData(data_name="Ventral view")
except Exception as e:
    print(e)
    raise


# Print the x coordinate of the head at frame 200 
print(td_sideview.data["head"].x[200])