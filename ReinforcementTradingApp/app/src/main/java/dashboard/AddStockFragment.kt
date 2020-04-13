package com.example.reinforcementtradingapp.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.retrofit.ReinforcementTradingAPI
import com.google.firebase.auth.FirebaseAuth
import io.reactivex.disposables.CompositeDisposable
import kotlinx.android.synthetic.main.add_stock_fragment.*
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.security.AuthProvider

class AddStockFragment : Fragment() {

    private var presenter: StocksMainDashboardPresenter = StocksMainDashboardPresenter()
    private var compositeDisposable: CompositeDisposable? = CompositeDisposable()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? =
        inflater.inflate(R.layout.add_stock_fragment, container, false)


    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        trade_button.setOnClickListener {
            createTransaction(enter_stock_edit_text.toString(),
                enter_amount_edit_text.toString(), enter_percent_loss_edit_text.toString())
        }
    }

    private fun createTransaction(ticker: String, amount: String, loss: String) {
        ReinforcementTradingAPI
            .service
            .createTransaction(presenter.createTransaction(ticker, amount, loss))
            .enqueue(object : Callback<ResponseBody> {
                override fun onFailure(call: Call<ResponseBody>, t: Throwable) {
                    println("---TTTT :: POST Throwable EXCEPTION:: " + t.message)
                }

                override fun onResponse(call: Call<ResponseBody>, response: Response<ResponseBody>) {
                    if (response.isSuccessful) {
                        val msg = response.body()?.string()
                        println("---TTTT :: POST msg from server :: " + msg)
                        Toast.makeText(context, msg, Toast.LENGTH_SHORT).show()
                    }
                }
            })
    }
}