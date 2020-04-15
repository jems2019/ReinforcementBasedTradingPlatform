package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize
@Parcelize
class Stock(
    val userId: String,
    val initialBalance: Int,
    val cumulativeBalance: Int,
    val stockTicker: String,
    val loss: Int,
    val totalShares: Int,
    val transactions: ArrayList<String>
): Parcelable