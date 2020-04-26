package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.android.parcel.Parcelize

@Parcelize
data class StockSentiment(
    @SerializedName("sentiment")
    val sentiment: HashMap<String, Float>
) : Parcelable