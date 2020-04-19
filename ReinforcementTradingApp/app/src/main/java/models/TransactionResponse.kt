package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize

@Parcelize
class TransactionResponse(
    val success: Boolean,
    val transactions: HashMap<String,Transaction>
) : Parcelable
