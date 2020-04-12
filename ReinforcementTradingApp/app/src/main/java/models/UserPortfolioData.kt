package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize

@Parcelize
class UserPortfolioData(val stocks: HashMap<String, Stock>) : Parcelable