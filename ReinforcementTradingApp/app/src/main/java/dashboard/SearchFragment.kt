package com.example.reinforcementtradingapp.dashboard

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.appcompat.widget.SearchView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.DividerItemDecoration
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.SearchStockReviewActivity
import com.example.reinforcementtradingapp.dashboard.Adapters.SearchStockAdapter
import com.example.reinforcementtradingapp.retrofit.ReinforcementTradingAPI
import io.reactivex.schedulers.Schedulers
import kotlinx.android.synthetic.main.search_fragment.*
import kotlinx.android.synthetic.main.search_stock_review_layout.*

class SearchFragment : Fragment() {

    private lateinit var linearLayoutManager: LinearLayoutManager
    private var searchStockList: ArrayList<String> = ArrayList()
    private lateinit var adapter: SearchStockAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? =
        inflater.inflate(R.layout.search_fragment, container, false)


    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        linearLayoutManager = LinearLayoutManager(context)
        searchStockList.add("AAPL")
        searchStockList.add("AMZN")
        searchStockList.add("FB")
        searchStockList.add("MSFT")

        search_results_recycler_view.layoutManager = linearLayoutManager
        adapter = SearchStockAdapter(context!!, searchStockList)
        { stockTicker->
            val intent = Intent(context, SearchStockReviewActivity::class.java)
            intent.putExtra("stock_ticker", stockTicker)
            activity?.finish()
            startActivity(intent)
        }
        search_results_recycler_view.adapter = adapter
        search_results_recycler_view.addItemDecoration(DividerItemDecoration(context, LinearLayoutManager.HORIZONTAL))
        search_stock.queryHint = "Enter Stock Ticker Symbol"
        search_stock.setOnQueryTextListener(object : SearchView.OnQueryTextListener{
            override fun onQueryTextSubmit(query: String?): Boolean {
                TODO("Not yet implemented")
            }

            override fun onQueryTextChange(newText: String?): Boolean {
                adapter.filter.filter(newText)
                return false
            }
        })
    }
}