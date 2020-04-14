package com.example.reinforcementtradingapp

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.view.WindowManager
import androidx.appcompat.app.AppCompatActivity
import com.example.reinforcementtradingapp.dashboard.AddStockFragment
import com.example.reinforcementtradingapp.dashboard.StocksMainDashboardActivity
import com.example.reinforcementtradingapp.models.StockInfo
import com.example.reinforcementtradingapp.retrofit.ReinforcementTradingAPI
import com.google.firebase.auth.FirebaseAuth
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.disposables.CompositeDisposable
import io.reactivex.schedulers.Schedulers
import kotlinx.android.synthetic.main.search_stock_review_layout.*
import rx.Scheduler
import java.util.concurrent.TimeUnit

@SuppressLint("LongLogTag", "ResourceType")
class SearchStockReviewActivity : AppCompatActivity() {

    private val compositeDisposable: CompositeDisposable = CompositeDisposable()
    private lateinit var stockTicker: String

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.search_stock_review_layout)
        stockTicker = intent.getStringExtra("stock_ticker")
        progressBar1.visibility = View.VISIBLE
        trade_from_search.setOnClickListener {
            val intent = Intent(this, SearchStockReviewActivity::class.java)
            intent.putExtra("current_user", FirebaseAuth.getInstance().currentUser)
            intent.putExtra("fragment_to_load", "AddStock")
            startActivity(intent)
        }
        window.setFlags(
            WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE,
            WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE);
        getRealTimeDataSubscription(stockTicker)
    }


    private fun getRealTimeDataSubscription(stockTicker: String) {
        compositeDisposable.add(ReinforcementTradingAPI.service.getRealTimeData(stockTicker.toLowerCase())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribeOn(Schedulers.io())
            .subscribe({stockInfo ->
                getRealTimeTradeRecommendation(stockTicker, stockInfo)

            },{ throwable: Throwable ->
                Log.e("SearchStockReviewActivity", throwable.toString())

            }))
    }

    private fun getRealTimeTradeRecommendation(stockTicker: String, stockInfo: StockInfo) {
        compositeDisposable.add(ReinforcementTradingAPI.service.getRealTimeAction(stockTicker, stockInfo.date)
            .observeOn(AndroidSchedulers.mainThread())
            .subscribeOn(Schedulers.io())
            .subscribe({tradeAction ->
                search_review_ticker.text = String.format(resources.getString(R.string.stock_ticker), stockTicker)
                search_review_close.text = String.format(resources.getString(R.string.stock_close),
                    stockInfo.close
                )
                search_review_high.text = String.format(resources.getString(R.string.stock_high), stockInfo.high)
                search_review_open.text = String.format(resources.getString(R.string.stock_open), stockInfo.open)
                search_review_low.text = String.format(resources.getString(R.string.stock_low), stockInfo.low)
                search_review_volume.text = String.format(resources.getString(R.string.stock_volume), stockInfo.volume)
                search_review_recommendation.text = String.format(resources.getString(R.string.stock_recomendation), tradeAction.action)
                progressBar1.visibility = View.GONE
            },{throwable: Throwable ->
                Log.e("SearchStockReviewActivity", throwable.toString())
            }))
    }
}