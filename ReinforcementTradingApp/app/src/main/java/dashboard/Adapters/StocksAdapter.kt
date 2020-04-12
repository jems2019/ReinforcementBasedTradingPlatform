package com.example.reinforcementtradingapp.dashboard.Adapters

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.models.Stock
import kotlinx.android.synthetic.main.stocks_row.view.*

class StocksAdapter(val stocks: ArrayList<Stock>, val context: Context) :
    RecyclerView.Adapter<StocksAdapter.ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(
            LayoutInflater.from(context).inflate(R.layout.stocks_row, parent, false)
        )
    }

    override fun getItemCount(): Int {
        return stocks.size
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.stockTicker.text = stocks.get(position).stockTicker
        holder.numShares.text = stocks.get(position).totalShares.toString()
    }

   class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val stockTicker: TextView = view.portfolio_stock_ticker
        val numShares: TextView = view.portfolio_num_shares
    }
}