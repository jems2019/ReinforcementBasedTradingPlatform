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
import io.reactivex.android.schedulers.AndroidSchedulers
import io.reactivex.disposables.CompositeDisposable
import io.reactivex.schedulers.Schedulers
import kotlinx.android.synthetic.main.add_stock_fragment.*
import okhttp3.ResponseBody
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import rx.Scheduler
import java.security.AuthProvider

class AddStockFragment : Fragment() {

    private var presenter: StocksMainDashboardPresenter = StocksMainDashboardPresenter()
    private val compositeDisposable: CompositeDisposable = CompositeDisposable()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? =
        inflater.inflate(R.layout.add_stock_fragment, container, false)


    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        trade_button.setOnClickListener {
            createTransaction(enter_stock_edit_text.text.toString(),
                Integer.parseInt(enter_amount_edit_text.text.toString()), Integer.parseInt(enter_percent_loss_edit_text.text.toString()))
        }
    }

    private fun createTransaction(ticker: String, amount: Int, loss: Int) {
        compositeDisposable.add(ReinforcementTradingAPI.service.createTransaction(presenter.createTransaction(ticker, amount, loss))
            .observeOn(AndroidSchedulers.mainThread())
            .subscribeOn(Schedulers.io())
            .subscribe({transaction ->
                Toast.makeText(context, transaction.docId + " " + transaction.transactionStatus, Toast.LENGTH_SHORT).show()
                enter_amount_edit_text.text.clear()
                enter_percent_loss_edit_text.text.clear()
                enter_stock_edit_text.text.clear()
            },{

            }))
    }
}