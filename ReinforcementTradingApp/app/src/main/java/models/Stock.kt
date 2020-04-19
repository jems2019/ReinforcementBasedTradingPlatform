package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize
@Parcelize
class Stock(
    val userId: String,
    val autoTrade: Boolean,
    val initialBalance: String,
    val minBalance: String,
    val balance: Double,
    val stockTicker: String,
    val sharesHeld: Int,
    val transactions: ArrayList<String>
): Parcelable