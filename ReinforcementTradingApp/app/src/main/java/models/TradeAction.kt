package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize

@Parcelize
class TradeAction(
    val action: String,
    val percent: String
): Parcelable
