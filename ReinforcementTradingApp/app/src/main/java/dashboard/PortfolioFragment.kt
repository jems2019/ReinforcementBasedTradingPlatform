package com.example.reinforcementtradingapp.dashboard

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.DividerItemDecoration
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.dashboard.Adapters.StocksAdapter
import com.example.reinforcementtradingapp.models.Stock
import com.example.reinforcementtradingapp.models.UserPortfolioData
import com.example.reinforcementtradingapp.retrofit.ReinforcementTradingAPI
import com.google.firebase.auth.FirebaseUser
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.disposables.CompositeDisposable
import io.reactivex.schedulers.Schedulers
import kotlinx.android.synthetic.main.portfolio_fragment.*


class PortfolioFragment : Fragment(){
    private lateinit var userPortfolioData: UserPortfolioData
    private lateinit var user: FirebaseUser
    private var stocks: ArrayList<Stock> = ArrayList()
    private lateinit var linearLayoutManager: LinearLayoutManager
    private val compositeDisposable: CompositeDisposable = CompositeDisposable()


    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View?{
        user = activity?.intent?.getParcelableExtra("current_user")!!
        return inflater.inflate(R.layout.portfolio_fragment, container, false)
    }


    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        getNumberStocksSubscription()
        val myDivider =
            DividerItemDecoration(context, DividerItemDecoration.VERTICAL)
        myDivider.setDrawable(ContextCompat.getDrawable(context!!, R.drawable.divider)!!)
        portfolio_stocks_recycler_view.addItemDecoration(myDivider)
    }

    private fun getNumberStocksSubscription() {
        compositeDisposable.add(ReinforcementTradingAPI.service.getPortfolioData(user.uid)
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe({userPortfolioData ->
                if(userPortfolioData.found)
                    userPortfolioData.stocks.forEach{
                        stocks.add(it.value)
                    }
                linearLayoutManager = LinearLayoutManager(context)
                portfolio_stocks_recycler_view.layoutManager = linearLayoutManager
                portfolio_stocks_recycler_view.adapter =
                    StocksAdapter(
                        stocks,
                        context!!
                    ) {
                        val intent = Intent(context, ReviewStockTradeActivity::class.java)
                        intent.putExtra("current_user", user)
                        intent.putExtra("stock", it)
                        startActivity(intent)
                    }

            },{ throwable: Throwable ->
                Log.e("PortfolioFragment", throwable.toString())

            }))
    }
}