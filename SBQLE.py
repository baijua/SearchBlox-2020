### SearchBlox Query Log Explorer ###

# Libraries used
import streamlit as st
import numpy as np
import pandas as pd
import datetime as dt

st.title('SearchBlox Query Log Explorer')

DATE_COLUMN = 'created'

# Function to load and format data
def load_data(filename):
    data = pd.read_csv(filename, index_col = 0)

    # Select date segment of date and time string
    data[DATE_COLUMN] = data[DATE_COLUMN].map(lambda x: x[0:10])
    
    # Convert date column to datetime type
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])

    # Drop unnecessary columns, capitalize column names
    data.drop(columns = ["collection", "ip"], axis = 1, inplace = True)
    data.rename(columns = {"created" : "Date", "querystring" : "Query", "hits" : "Hits"}, inplace = True)
    
    # Set date column as dataframe index
    data = data.set_index('Date')

    # Remove null/blank values
    data.dropna()

    # Sort dataframe by date
    data.sort_index(inplace = True)
    return data

# Upload CSV file, checks validity
filecheck = 1
file = st.file_uploader("Choose a CSV file: ", type = 'CSV')
if file is not None:
    data_load_state = st.text('Loading data...')
    rawdata = load_data(file) # call load data function
    data_load_state.text('Loading data...done!')
    filecheck = 0

# If valid file
if filecheck == 0:
    st.write('The raw data contains ', len(rawdata.index), ' searches.')

    # Default values for date range inputs
    daterangestart = rawdata.index.min().date()
    daterangeend = dt.date.today()

    # User input to set date range
    st.subheader('Date Configuration')
    startdate = st.date_input('Start date: ', daterangestart)
    enddate = st.date_input('End date: ', daterangeend)

    # Checks date range validity
    if (startdate == daterangestart or startdate > daterangestart) & (startdate < enddate) & (enddate == daterangeend or enddate < daterangeend):
        datecheck = 0
    else:
        st.error('Error: End date must fall after start date.')
        datecheck = 1

    # If dates are valid, selects data from inputted range
    if datecheck == 1:
        st.write("Please fix the dates above.")
    elif datecheck == 0:
        datedf = rawdata.loc[startdate:enddate]

        # Displays date range and number of searches
        st.success('Start date: `%s`\n\nEnd date:`%s`' % (daterangestart, enddate))
        st.write('There were ', len(datedf.index), ' searches from `%s` to `%s`.' % (startdate, enddate))
    
        # Buttons to display top queries from date range
        n = 0
        if st.button('Top 10 Searches'):
            n = 10
            df10 = datedf.Query.value_counts()[:n]
            st.write(df10)
        if st.button('Top 25 Searches'):
            n = 25
            df25 = datedf.Query.value_counts()[:n]
            st.write(df25)
        if st.button('Top 100 Searches'):
            n = 100
            df100 = datedf.Query.value_counts()[:n]
            st.write(df100)

        # User input for query string to search from date range
        st.subheader("Query Search")
        matchword = st.text_input('', "")
        if matchword != "":
            searchdf = datedf[datedf.Query.str.contains(matchword, case = False, na = False)]
            st.write('There were ', len(searchdf.index), ' searches containing "', matchword, '" from `%s` to `%s`.' % (startdate, enddate))
        
            # Checkbox to display dataframe of searched query
            showdf = st.checkbox("Show dataframe")
            if showdf:
                st.write(searchdf)
        else:
            st.write("Please enter a query to search.")

# Invalid file or file not uploaded
else:
    st.write("Please upload a file to use the explorer.")