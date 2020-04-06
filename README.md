Step 1
Run flask_app.py

Step 2
Open ReinforcementBasedTradingPlatform/build.gradle in Android Studio

Step 3
Change the IP address in 

companion object {
        private val retrofit = Retrofit.Builder()
                .baseUrl("http://Your IP ADDRESS:5000")
                .addConverterFactory(GsonConverterFactory.create(GsonBuilder().create()))
                .build()
                
#API docs: 
 ## realtime stock and sentiment API
    - API endpoint:
        - /get_stock
    - parameters:
        - "start_year": 2020,
	    - "end_year":2020,
	    - "start_month": 1,
	    - "end_month": 1,
	    - "start_day": 1,
	    - "end_day": 10,
	    - "ticker": "AAPL"
    - return packet
        - json string of a dataframe
            - Columns format:
                - Date
                - Open
                - Close
                - volume
                - high
                 -low
                 -Sentiment Score
        - packet:
            - {"Date":{"0":"2019-12-31T00:00:00.000Z",
                       "1":"2020-01-02T00:00:00.000Z",
                       "2":"2020-01-03T00:00:00.000Z"},
               "SentimentScore":{"0":0.07664,"1":0.0,"2":0.1514266667},
               "Open":{"0":"289.9300","1":"296.2400","2":"297.1500"},
               "High":{"0":"293.6800","1":"300.6000","2":"300.5800"},
               "Low":{"0":"289.5200","1":"295.1900","2":"296.5000"},
               "Close":{"0":"293.6500","1":"300.3500","2":"297.4300"},
               "Volume":{"0":"25247625","1":"33911864","2":"36633878"}}
     
