package com.example.reinforcementtradingapp

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import kotlinx.android.synthetic.main.search_stock_review_layout.*

class SearchStockReviewActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.search_stock_review_layout)

        toolbar_review_stock.setNavigationOnClickListener {
            onBackPressed()
        }
    }
}