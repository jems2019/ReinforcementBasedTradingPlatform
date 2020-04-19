package com.example.reinforcementtradingapp.dashboard.Adapters

import android.content.Context
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.models.Stock
import com.example.reinforcementtradingapp.models.Transaction
import kotlinx.android.synthetic.main.transaction_row.view.*
import java.math.RoundingMode

class TransactionsAdapter(val transactions: ArrayList<Transaction>, val context: Context, val listener: (Stock) -> Unit) :
    RecyclerView.Adapter<TransactionsAdapter.ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        return ViewHolder(
            LayoutInflater.from(context).inflate(R.layout.transaction_row, parent, false)
        )
    }

    override fun getItemCount(): Int {
        return transactions.size
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.transactionType.text = transactions[position].actionType + transactions[position].sharesTransacted
        holder.transactionDate.text = transactions[position].timestamp.substringBefore("at")
    }

   class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val transactionType: TextView = view.transaction_type
        val transactionDate: TextView = view.transaction_date

    }
}