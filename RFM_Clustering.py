import sys, getopt
import pandas as pd
from datetime import datetime

def main():
   inputfile = 'sample-orders.csv'
   outputfile = 'rfm-segmentation.csv'
   inputdate = '2014-12-31'
   rfm(inputfile, outputfile, inputdate)


def rfm(inputfile, outputfile, inputdate):
   print(" ")
   print("---------------------------------------------")
   print(" Calculating RFM segmentation for " + inputdate)
   print("---------------------------------------------")

   NOW = datetime.strptime(inputdate, "%Y-%m-%d")

   # Open orders file
   orders = pd.read_csv(inputfile, sep=',', encoding='latin1')
   orders['order_date'] = pd.to_datetime(orders['order_date'])
   
   rfmTable = orders.groupby('customer').agg({'order_date': lambda x: (NOW - x.max()).days, # Recency
                                              'order_id': lambda x: len(x),      # Frequency
                                              'grand_total': lambda x: x.sum()}) # Monetary Value

   rfmTable['order_date'] = rfmTable['order_date'].astype(int)
   rfmTable.rename(columns={'order_date': 'recency', 
                              'order_id': 'frequency', 
                              'grand_total': 'monetary_value'}, inplace=True)


   quantiles = rfmTable.quantile(q=[0.25,0.5,0.75])
   quantiles = quantiles.to_dict()

   rfmSegmentation = rfmTable

   rfmSegmentation['R_Quartile'] = rfmSegmentation['recency'].apply(RClass, args=('recency',quantiles,))
   rfmSegmentation['F_Quartile'] = rfmSegmentation['frequency'].apply(FMClass, args=('frequency',quantiles,))
   rfmSegmentation['M_Quartile'] = rfmSegmentation['monetary_value'].apply(FMClass, args=('monetary_value',quantiles,))

   rfmSegmentation['RFMClass'] = rfmSegmentation.R_Quartile.map(str) + rfmSegmentation.F_Quartile.map(str) + rfmSegmentation.M_Quartile.map(str)
   rfmSegmentation['Segment'] = rfmSegmentation.apply(AssignSegments, axis=1)
   rfmSegmentation.to_csv(outputfile, sep=',')

   print(" ")
   print(" DONE! Check %s" % (outputfile))
   print(" ")

# We create two classes for the RFM segmentation since, being high recency is bad, while high frequency and monetary value is good. 
# Arguments (x = value, p = recency, monetary_value, frequency, k = quartiles dict)
def RClass(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]: 
        return 3
    else:
        return 4
    
# Arguments (x = value, p = recency, monetary_value, frequency, k = quartiles dict)
def FMClass(x,p,d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]: 
        return 2
    else:
        return 1

def AssignSegments(row):
    val = 'Others'
    if row['R_Quartile'] == 1 and row['F_Quartile'] == 1 and row['M_Quartile'] == 1:
        val = 'Best Customers'
    elif (row['R_Quartile'] == 1 or row['R_Quartile'] == 2 or row['R_Quartile'] == 3 or row['R_Quartile'] == 4) and row['F_Quartile'] == 1 and (row['M_Quartile'] == 1 or row['M_Quartile'] == 2 or row['M_Quartile'] == 3 or row['M_Quartile'] == 4):
        val = 'Loyal Customers'
    
    
    
    elif row['R_Quartile'] == 1 and (row['F_Quartile'] == 1 or row['F_Quartile'] == 2 or row['F_Quartile'] == 3 or row['F_Quartile'] == 4) and (row['M_Quartile'] == 1 or row['M_Quartile'] == 2 or row['M_Quartile'] == 3 or row['M_Quartile'] == 4):
        val = 'Recent Customers'
        
        
        
    elif (row['R_Quartile'] == 1 or row['R_Quartile'] == 2 or row['R_Quartile'] == 3 or row['R_Quartile'] == 4) and (row['F_Quartile'] == 1 or row['F_Quartile'] == 2 or row['F_Quartile'] == 3 or row['F_Quartile'] == 4) and row['M_Quartile'] == 1:
        val = 'Big Spenders'
    elif row['R_Quartile'] == 3 and row['F_Quartile'] == 1 and row['M_Quartile'] == 1:
        val = 'Almost Lost'
    elif row['R_Quartile'] == 4 and row['F_Quartile'] == 1 and row['M_Quartile'] == 1:
        val = 'Lost Customers'
    elif row['R_Quartile'] == 4 and row['F_Quartile'] == 4 and row['M_Quartile'] == 4:
        val = 'Lost Cheap Customers'
    
    return val

if __name__ == "__main__":
   main()
