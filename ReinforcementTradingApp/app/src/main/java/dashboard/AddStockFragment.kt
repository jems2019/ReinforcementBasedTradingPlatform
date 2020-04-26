package com.example.reinforcementtradingapp.dashboard

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.example.reinforcementtradingapp.R
import com.example.reinforcementtradingapp.models.UserData
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

    private val compositeDisposable: CompositeDisposable = CompositeDisposable()
    private lateinit var userData: UserData

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? =
        inflater.inflate(R.layout.add_stock_fragment, container, false)


    override fun onActivityCreated(savedInstanceState: Bundle?) {
        super.onActivityCreated(savedInstanceState)
        userData = activity?.intent?.getParcelableExtra("stocks")!!
        trade_button.setOnClickListener {
            if(userData.stocks.contains(enter_stock_edit_text.text.toString())) {
                updateStockForUserSubscription()
            } else {
                addStockForUserSubscription()
            }
        }
    }

    private fun addStockForUserSubscription() {
       compositeDisposable.add(ReinforcementTradingAPI.service.addStockToUser(FirebaseAuth.getInstance().uid!!, enter_stock_edit_text.text.toString().toUpperCase(),
       enter_amount_edit_text.text.toString().toDouble(), enter_percent_loss_edit_text.text.toString().toDouble())
           .observeOn(AndroidSchedulers.mainThread())
           .subscribeOn(Schedulers.io())
           .subscribe({
               clearFields()
               userData.stocks.add(enter_stock_edit_text.text.toString())
               Toast.makeText(context, "Added stock to User", Toast.LENGTH_SHORT).show()
           },{ throwable: Throwable ->
               Log.e("AddStockFragment", throwable.toString())

           }))
    }

    private fun updateStockForUserSubscription() {
        compositeDisposable.add(ReinforcementTradingAPI.service.updateStockForUser(FirebaseAuth.getInstance().uid!!, enter_stock_edit_text.text.toString().toUpperCase(),
            enter_amount_edit_text.text.toString().toDouble(), enter_percent_loss_edit_text.text.toString().toDouble())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribeOn(Schedulers.io())
            .subscribe({
                    clearFields()
                    Toast.makeText(context, "Updated Stock Balances", Toast.LENGTH_SHORT).show()
            },{ throwable: Throwable ->
                Log.e("AddStockFragment", throwable.toString())

            }))
    }

    private fun clearFields() {
        enter_amount_edit_text.text.clear()
        enter_percent_loss_edit_text.text.clear()
        enter_stock_edit_text.text.clear()
    }
}