package com.example.reinforcementtradingapp.models

import android.os.Parcelable
import kotlinx.android.parcel.Parcelize

@Parcelize
class UserData(
    val found: Boolean,
    val stocks: ArrayList<String>
): Parcelable