package com.example.reinforcementtradingapp.retrofit

import com.google.gson.GsonBuilder
import com.google.gson.JsonObject
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*



class ReinforcementTradingAPI {

    interface APIService {
        @GET("/users/{user}")
        fun greetUser(@Path("user") user: String): Call<ResponseBody>

        @Headers("Content-type: application/json")
        @POST("/api/post_some_data")
        fun getVectors(@Body body: JsonObject): Call<ResponseBody>

        @Headers("Content-type: application/json")
        @POST("/api/create_transaction")
        fun createTransaction(@Body body: JsonObject): Call<ResponseBody>
    }

    companion object {
        private val retrofit = Retrofit.Builder()
                .baseUrl("http://10.0.2.2:5000")
                .addConverterFactory(GsonConverterFactory.create(GsonBuilder().create()))
                .build()

        var service = retrofit.create(APIService::class.java)
    }
}