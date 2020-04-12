package com.example.reinforcementtradingapp.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.appcompat.widget.SearchView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.dashboard.Adapters.SearchStockAdapter
import kotlinx.android.synthetic.main.search_fragment.*

class SearchFragment : Fragment() {

    private lateinit var linearLayoutManager: LinearLayoutManager
    private lateinit var searchStockList: ArrayList<String>
    private lateinit var adapter: SearchStockAdapter

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? =
        inflater.inflate(R.layout.search_fragment, container, false)


    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        linearLayoutManager = LinearLayoutManager(context)
        searchStockList.add("AAPL")
        searchStockList.add("AMZN")
        searchStockList.add("FB")
        searchStockList.add("MSFT")

        search_results_recycler_view.layoutManager = linearLayoutManager
        adapter = SearchStockAdapter(context!!, searchStockList)
        search_results_recycler_view.adapter = adapter
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