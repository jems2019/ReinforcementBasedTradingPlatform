package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.android.parcel.Parcelize

@Parcelize
class Transaction(
    @SerializedName("action_type")
    val actionType: String,
    val amount: Double,
    val portfolioValue: Double,
    val sharesTransacted: Int,
    val stockTicker: String,
    val timestamp: String
): Parcelable