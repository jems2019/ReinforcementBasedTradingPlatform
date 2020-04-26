package com.example.reinforcementtradingapp.retrofit


import android.content.Context
import com.chuckerteam.chucker.api.ChuckerInterceptor
import com.example.reinforcementtradingapp.models.*
import com.google.gson.GsonBuilder
import com.google.gson.JsonObject
import com.jakewharton.retrofit2.adapter.rxjava2.RxJava2CallAdapterFactory
import io.reactivex.Single
import okhttp3.OkHttpClient
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import java.util.concurrent.TimeUnit
import kotlin.coroutines.coroutineContext


class ReinforcementTradingAPI {

    interface APIService {
        @GET("/users/{user}")
        fun greetUser(@Path("user") user: String): Call<ResponseBody>

        @Headers("Content-type: application/json")
        @POST("/api/post_some_data")
        fun getVectors(@Body body: JsonObject): Call<ResponseBody>

        @Headers("Content-type: application/json")
        @POST("/api/create_transaction")
        fun createTransaction(@Body transactionBody: TransactionResponse): Single<Transaction>

        @GET("/api/check_user/{userId}")
        fun checkIfUserExists(@Path("userId") userId: String): Call<ResponseBody>

        @GET("/api/get_portfolio_data/{userId}")
        fun getPortfolioData(@Path("userId") userId: String): Single<UserPortfolioData>

        @GET("/api/get_id_data/")
        fun getRealTimeData(@Query("ticker") ticker: String): Single<StockInfo>

        @GET("/api/get_rl_action/")
        fun getRealTimeAction(@Query("ticker") ticker: String,
                              @Query ("date") date: String): Single<TradeAction>

        @GET("/api/get_transactions/")
        fun getTransactions(@Query("userId") userId: String,
                            @Query("ticker") ticker: String): Single<TransactionResponse>

        @POST("/api/update_stock_for_user/")
        fun updateStockForUser(@Query("userId") userId: String,
                               @Query("ticker") ticker: String,
                               @Query("amount") amount: Double,
                               @Query("minBalance") minBalance: Double): Single<ResponseBody>

        @POST("/api/add_stock_to_user/")
        fun addStockToUser(@Query("userId") userId: String,
                           @Query("ticker") ticker: String,
                           @Query("amount") amount: Double,
                           @Query("minBalance") minBalance: Double): Single<ResponseBody>

    }

    companion object {
        var client = OkHttpClient.Builder()
            .connectTimeout(100, TimeUnit.SECONDS)
            .readTimeout(100, TimeUnit.SECONDS).build()

        private val retrofit = Retrofit.Builder()
                .baseUrl("http://10.0.2.2:5000").client(client)
//                .baseUrl("https://reinforcementtradingplatform.web.app")
                .addConverterFactory(GsonConverterFactory.create(GsonBuilder().create()))
                .addCallAdapterFactory(RxJava2CallAdapterFactory.create())
                .build()

        var service = retrofit.create(APIService::class.java)
    }
}