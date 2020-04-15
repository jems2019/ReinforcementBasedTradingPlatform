package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize

@Parcelize
class UserPortfolioData(
    val found: Boolean, val stocks: HashMap<String, Stock>) : Parcelable


