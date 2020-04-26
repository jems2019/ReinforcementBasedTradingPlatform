package com.example.reinforcementtradingapp.dashboard.Adapters

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Filter
import android.widget.Filterable
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.DividerItemDecoration
import androidx.recyclerview.widget.RecyclerView
import com.example.reinforcementtradingapp.R
import kotlinx.android.synthetic.main.search_stock_row.view.*

class SearchStockAdapter(private val context: Context, private var stocks: ArrayList<String>, private val listener: (String) -> Unit) : RecyclerView.Adapter<SearchStockAdapter.ViewHolder>(), Filterable {

    var stocksFilterList = ArrayList<String>()

    init {
        stocksFilterList = stocks
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(LayoutInflater.from(context).inflate(R.layout.search_stock_row,
            parent, false))
    }

    override fun getItemCount(): Int {
        return stocksFilterList.size
    }

    override fun onBindViewHolder(holder: SearchStockAdapter.ViewHolder, position: Int) {
        holder?.search?.text =  stocksFilterList[position]
        holder.itemView.setOnClickListener {
            listener.invoke(stocksFilterList[position])
        }
    }

    class ViewHolder(inflate: View?) : RecyclerView.ViewHolder(inflate!!) {
        val search = inflate?.search_stock_ticker
    }

    override fun getFilter(): Filter {
        return object : Filter() {
            override fun performFiltering(constraint: CharSequence?): FilterResults {
                val charSearch = constraint.toString().toUpperCase()
                stocksFilterList = if(charSearch.isEmpty()) {
                    ArrayList()
                } else {
                    val results = ArrayList<String>()
                    for(stock in stocks) {
                        if(stock.contains(charSearch)) {
                            results.add(stock)
                        }
                    }
                    results
                }
                val filterResults = FilterResults()
                filterResults.values = stocksFilterList
                return filterResults
            }

            @Suppress("UNCHECKED_CAST")
            override fun publishResults(constraint: CharSequence?, results: FilterResults?) {
                stocksFilterList = results?.values as ArrayList<String>
                notifyDataSetChanged()
            }

        }
    }

}