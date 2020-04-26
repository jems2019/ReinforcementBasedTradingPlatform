package com.example.reinforcementtradingapp.dashboard.Adapters

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.models.Stock
import kotlinx.android.synthetic.main.stocks_row.view.*
import java.math.RoundingMode

class StocksAdapter(val stocks: ArrayList<Stock>, val map: HashMap<String, Float>, val context: Context, val listener: (Stock) -> Unit) :
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
        var isSharesHeld = true
        holder.stockTicker.text = stocks[position].stockTicker
        holder.numShares.text = stocks[position].sharesHeld.toString()
        holder.stockTicker.setOnClickListener {
            listener.invoke(stocks[position])
        }
        holder.numShares.setOnClickListener {
            if(isSharesHeld) {
                holder.numShares.text = "$" + stocks[position].balance.toBigDecimal().setScale(2, RoundingMode.HALF_EVEN).toString()
                isSharesHeld = false
            }
            else {
                holder.numShares.text = stocks[position].sharesHeld.toString()
                isSharesHeld = true
            }
        }

        map[stocks[position].stockTicker]?.let {sentiment ->
            if(sentiment > 0) {
                holder.numShares.setBackgroundColor(ContextCompat.getColor(context, R.color.light_green))
            } else {
                holder.numShares.setBackgroundColor(ContextCompat.getColor(context, R.color.light_red))
            }
        }
    }

   class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val stockTicker: TextView = view.portfolio_stock_ticker
        val numShares: TextView = view.portfolio_num_shares

    }
}