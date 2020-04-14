package com.example.reinforcementtradingapp.dashboard

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.dashboard.Adapters.StocksAdapter
import com.example.reinforcementtradingapp.models.Stock
import com.example.reinforcementtradingapp.models.UserPortfolioData
import com.example.reinforcementtradingapp.retrofit.ReinforcementTradingAPI
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.disposables.CompositeDisposable
import kotlinx.android.synthetic.main.portfolio_fragment.*
import com.google.firebase.auth.FirebaseUser as FirebaseUser

class PortfolioFragment : Fragment(){
    private lateinit var userPortfolioData: UserPortfolioData
    private lateinit var user: FirebaseUser
    private lateinit var stocks: ArrayList<Stock>
    private lateinit var linearLayoutManager: LinearLayoutManager
    private val compositeDisposable: CompositeDisposable = CompositeDisposable()


    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View?{
        user = activity?.intent?.getParcelableExtra("current_user")!!
        return inflater.inflate(R.layout.portfolio_fragment, container, false)
    }


    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        getNumberStocksSubscription()
    }

    private fun getNumberStocksSubscription() {
        compositeDisposable.add(ReinforcementTradingAPI.service.getPortfolioData(user.uid)
            .subscribeOn(AndroidSchedulers.mainThread())
            .subscribe({userPortfolioData ->
                userPortfolioData.stocks.forEach{
                    stocks.add(it.value)
                }
                linearLayoutManager = LinearLayoutManager(context)
                portfolio_stocks_recycler_view.layoutManager = linearLayoutManager
                portfolio_stocks_recycler_view.adapter =
                    StocksAdapter(
                        stocks,
                        context!!
                    ) {}

            },{ throwable: Throwable ->
                Log.e("PortfolioFragment", throwable.toString())

            }))
    }
}