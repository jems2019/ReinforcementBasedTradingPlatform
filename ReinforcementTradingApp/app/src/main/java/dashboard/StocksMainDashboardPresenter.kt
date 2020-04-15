package com.example.reinforcementtradingapp.dashboard

import com.example.reinforcementtradingapp.models.TransactionBody
import com.google.firebase.auth.FirebaseAuth
import com.google.gson.JsonObject

class StocksMainDashboardPresenter {

    fun createTransaction(ticker: String, amount: Int, loss: Int) : TransactionBody {
        return TransactionBody(FirebaseAuth.getInstance().uid!!, ticker, amount, loss)
    }
}