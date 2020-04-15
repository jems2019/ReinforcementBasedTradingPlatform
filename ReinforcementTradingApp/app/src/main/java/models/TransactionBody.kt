package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize

@Parcelize
class TransactionBody(
    val userId: String,
    val stockTicker: String,
    val amount: Int,
    val percentLoss: Int
) : Parcelable
