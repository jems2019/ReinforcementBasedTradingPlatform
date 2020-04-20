package com.example.reinforcementtradingapp.dashboard

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DividerItemDecoration
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.dashboard.Adapters.TransactionsAdapter
import com.example.reinforcementtradingapp.models.Stock
import com.example.reinforcementtradingapp.models.Transaction
import com.example.reinforcementtradingapp.models.TransactionResponse
import com.example.reinforcementtradingapp.retrofit.ReinforcementTradingAPI
import com.google.firebase.auth.FirebaseUser
import com.jjoe64.graphview.series.DataPoint
import com.jjoe64.graphview.series.LineGraphSeries
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.disposables.CompositeDisposable
import io.reactivex.schedulers.Schedulers
import kotlinx.android.synthetic.main.portfolio_fragment.*
import kotlinx.android.synthetic.main.review_stock_layout.*
import kotlinx.android.synthetic.main.stocks_row.*
import rx.Scheduler
import java.math.RoundingMode
import java.text.SimpleDateFormat
import java.time.LocalDate
import java.time.format.DateTimeFormatter

class ReviewStockTradeActivity : AppCompatActivity() {

    private val compositeDisposable: CompositeDisposable = CompositeDisposable()
    private lateinit var linearLayoutManager: LinearLayoutManager
    private lateinit var stock: Stock
    private lateinit var user: FirebaseUser
    private var transactions: ArrayList<Transaction> = ArrayList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.review_stock_layout)
        user = intent.getParcelableExtra("current_user")
        stock = intent.getParcelableExtra("stock")
        val myDivider =
            DividerItemDecoration(this, DividerItemDecoration.VERTICAL)
        myDivider.setDrawable(ContextCompat.getDrawable(this, R.drawable.divider)!!)
        review_stock_transactions_recycler_view.addItemDecoration(myDivider)
        getTransactionsSubscription()
    }

    override fun onBackPressed() {
        super.onBackPressed()
        finish()
    }

    private fun getTransactionsSubscription() {
        compositeDisposable.add(ReinforcementTradingAPI.service.getTransactions(user.uid, stock.stockTicker)
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe({ it ->
                it.transactions.forEach {
                    transactions.add(it.value)
                }
                setUpView()
            },{

            }))
    }

    private fun setUpView() {
        review_stock_ticker.text = stock.stockTicker
        initial_balance.text = String.format(resources.getString(R.string.initial_balance), stock.initialBalance.toBigDecimal().setScale(2, RoundingMode.HALF_EVEN).toString())
        stock_shares_held.text = String.format(resources.getString(R.string.portfolio_stock_shares_held), stock.sharesHeld.toString())
        stock_portfolio_value.text = String.format(resources.getString(R.string.portfolio_value), transactions[0].portfolioValue.toBigDecimal().setScale(2, RoundingMode.HALF_EVEN).toString())
        linearLayoutManager = LinearLayoutManager(applicationContext)
        review_stock_transactions_recycler_view.layoutManager = linearLayoutManager
        review_stock_transactions_recycler_view.adapter = TransactionsAdapter(
            transactions,
            this
        ) {}

//        var formatter = SimpleDateFormat("yyyy-MM-dd")
//
//        val dataPoints = emptyArray<DataPoint>()
//        transactions.forEachIndexed { index, transaction ->
//            var date = formatter.parse(transaction.timestamp.substringBefore(" "))
//            dataPoints[index] =
//                DataPoint(date, transaction.portfolioValue)
//        }
//        val series = LineGraphSeries<DataPoint>(dataPoints)
//        stock_review_graph.addSeries(series)

    }
}