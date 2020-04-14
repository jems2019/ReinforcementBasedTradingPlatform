package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize

@Parcelize
class StockInfo(
    val date: String,
    val open: String,
    val high: String,
    val low: String,
    val close: String,
    val volume: String
):Parcelable
