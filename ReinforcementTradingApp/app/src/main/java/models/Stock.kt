package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize
@Parcelize
class Stock(
    val userId: String,
    val balance: Int,
    val stockTicker: String,
    val totalShares: Int,
    val transactions: ArrayList<String>
): Parcelable