package com.example.reinforcementtradingapp.dashboard

import com.google.firebase.auth.FirebaseAuth
import com.google.gson.JsonObject

class StocksMainDashboardPresenter {

    fun createTransaction(ticker: String, amount: String, loss: String) : JsonObject {
        val jsonObj = JsonObject()
        jsonObj.addProperty("userId", FirebaseAuth.getInstance().uid)
        jsonObj.addProperty("stockTicker", ticker)
        jsonObj.addProperty("amount", amount)
        jsonObj.addProperty("percentLoss", loss)
        return JsonObject()
    }
}