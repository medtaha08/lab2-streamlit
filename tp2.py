import numpy as np
temp=np.array([12,14,15,18,19,
               33,31,45,16,17,
               13,25,20,np.nan,11,
               ])
print(temp.dtype)
print(temp.ndim)
print(temp.shape)
print(temp.size)
min=temp[0]
max=temp[-1]
s1=temp[:14]
s2=temp[15:]
temp1=temp>25 
temp_haut=temp[temp1]
temp2=(temp>=18) & (temp<=25)
temp_=np.where(temp2)
temp_moy=np.nanmean(temp)
print(temp_moy)
temp_min=np.nanmin(temp)
print(temp_min)
temp_max=np.nanmax(temp)
temp_median=np.nanmedian(temp)
print(f"{temp_median}")
temp_ecarttype=np.nanstd(temp)
print(f"{temp_ecarttype:.2f}")
normalisation=(temp - temp_min) / (temp_max - temp_min) 
print(f"{normalisation}")