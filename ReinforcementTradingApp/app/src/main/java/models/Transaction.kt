package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.android.parcel.Parcelize

@Parcelize
class Transaction(
    @SerializedName("transaction_status")
    val transactionStatus: String,

    val docId: String
): Parcelable