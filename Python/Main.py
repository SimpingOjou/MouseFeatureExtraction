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

# Print the y coordinate of the anckle at frame 143 
print(td_sideview.data["anckle"].x[143])

# Print the likelihood for the left hindfinger tracking at the last frame 
print(td_sideview.data["lHindfingers"].x[-1])
