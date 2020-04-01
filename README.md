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
