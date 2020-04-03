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
     
