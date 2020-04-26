package com.example.reinforcementtradingapp.dashboard

import android.app.PendingIntent.getActivity
import android.os.Bundle
import android.view.View
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DividerItemDecoration
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.dashboard.Adapters.TransactionsAdapter
import com.example.reinforcementtradingapp.models.GraphData
import com.example.reinforcementtradingapp.models.Stock
import com.example.reinforcementtradingapp.models.Transaction
import com.example.reinforcementtradingapp.retrofit.ReinforcementTradingAPI
import com.google.firebase.auth.FirebaseUser
import com.jjoe64.graphview.GraphView
import com.jjoe64.graphview.helper.DateAsXAxisLabelFormatter
import com.jjoe64.graphview.series.DataPoint
import com.jjoe64.graphview.series.LineGraphSeries
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.disposables.CompositeDisposable
import io.reactivex.schedulers.Schedulers
import kotlinx.android.synthetic.main.review_stock_layout.*
import java.math.RoundingMode
import java.text.SimpleDateFormat
import java.util.*
import kotlin.collections.ArrayList
import kotlin.time.days


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
        progressBar_review_stock.visibility = View.VISIBLE
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
        if(transactions.isEmpty()) {
            review_stock_transactions_recycler_view.visibility = View.GONE
            stock_review_graph.visibility = View.GONE
            review_stock_ticker.text = stock.stockTicker
            transaction_text.visibility = View.GONE
            initial_balance.text = String.format(
                resources.getString(R.string.initial_balance),
                stock.initialBalance.toBigDecimal().setScale(2, RoundingMode.HALF_EVEN).toString()
            )
            stock_shares_held.text = String.format(
                resources.getString(R.string.portfolio_stock_shares_held),
                stock.sharesHeld.toString()
            )
            stock_portfolio_value.text = String.format(
                resources.getString(R.string.portfolio_value),
                stock.initialBalance.toBigDecimal().setScale(2, RoundingMode.HALF_EVEN).toString()
            )
        } else {

            var formatter = SimpleDateFormat("yyyy-MM-dd")
            transactions.sortBy { formatter.parse((it.timestamp.substringBefore(" "))) }
            review_stock_ticker.text = stock.stockTicker
            initial_balance.text = String.format(
                resources.getString(R.string.initial_balance),
                stock.initialBalance.toBigDecimal().setScale(2, RoundingMode.HALF_EVEN).toString()
            )
            stock_shares_held.text = String.format(
                resources.getString(R.string.portfolio_stock_shares_held),
                stock.sharesHeld.toString()
            )
            stock_portfolio_value.text = String.format(
                resources.getString(R.string.portfolio_value),
                transactions[transactions.size - 1].portfolioValue.toBigDecimal()
                    .setScale(2, RoundingMode.HALF_EVEN).toString()
            )
            linearLayoutManager = LinearLayoutManager(applicationContext)
            review_stock_transactions_recycler_view.layoutManager = linearLayoutManager
            review_stock_transactions_recycler_view.adapter = TransactionsAdapter(
                transactions.asReversed(),
                this
            ) {}

            val transactionMap =
                transactions.groupBy { formatter.parse((it.timestamp.substringBefore(" "))) }
            var transactionsList = ArrayList<GraphData>()
            for (transaction in transactionMap) {
                transactionsList.add(GraphData(transaction.key, transaction.value[transaction.value.size-1].portfolioValue))
            }

            transactionsList = if (transactionsList.size >= 5) {
                transactionsList.takeLast(5) as ArrayList<GraphData>
            } else {
                transactionsList
            }
            val dataPoints = arrayOfNulls<DataPoint>(transactionsList.size)
            transactionsList.forEachIndexed { index, transaction ->
                dataPoints[index] =
                    DataPoint(transaction.date, transaction.portfolioAmount)
            }
            val series = LineGraphSeries<DataPoint>(dataPoints)
            stock_review_graph.addSeries(series)
            stock_review_graph.title = "Portfolio Value over Last 5 Transactions"
            stock_review_graph.titleTextSize = 50f
            stock_review_graph.gridLabelRenderer.horizontalAxisTitle = "Date"
            stock_review_graph.gridLabelRenderer.verticalAxisTitle = "Portfolio Value($)"
            stock_review_graph.gridLabelRenderer.labelFormatter = DateAsXAxisLabelFormatter(this)
//            stock_review_graph.gridLabelRenderer.numHorizontalLabels = 4
//            stock_review_graph.viewport.setMinX(transactionsList[0].date.time.toDouble())
//            stock_review_graph.viewport.setMaxX(transactionsList[transactionsList.size - 1].date.time.toDouble())
//            stock_review_graph.viewport.isXAxisBoundsManual = true
            stock_review_graph.gridLabelRenderer.setHumanRounding(true)
        }
        progressBar_review_stock.visibility = View.GONE
    }
}