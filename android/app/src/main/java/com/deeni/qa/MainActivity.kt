package com.deeni.qa

import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.deeni.qa.api.AskRequest
import com.deeni.qa.api.AskResponse
import com.deeni.qa.api.ApiService
import com.deeni.qa.databinding.ActivityMainBinding
import com.deeni.qa.util.Pref
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding
    private lateinit var api: ApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupRetrofit()
        setupUi()
    }

    private fun setupRetrofit() {
        val baseUrl = Pref.getBaseUrl(this)
        val log = HttpLoggingInterceptor().apply { level = HttpLoggingInterceptor.Level.BASIC }
        val client = OkHttpClient.Builder().addInterceptor(log).build()
        api = Retrofit.Builder()
            .baseUrl(baseUrl)
            .addConverterFactory(MoshiConverterFactory.create())
            .client(client)
            .build()
            .create(ApiService::class.java)
    }

    private fun setupUi() {
        val languages = listOf("urdu", "english")
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, languages)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.languageSpinner.adapter = adapter

        binding.saveBaseUrl.setOnClickListener {
            val url = binding.baseUrlInput.text?.toString()?.trim()
            if (!url.isNullOrEmpty()) {
                Pref.setBaseUrl(this, url)
                Toast.makeText(this, "Base URL saved", Toast.LENGTH_SHORT).show()
                setupRetrofit()
            }
        }

        binding.askButton.setOnClickListener {
            val lang = binding.languageSpinner.selectedItem?.toString() ?: "urdu"
            val question = binding.questionInput.text?.toString()?.trim() ?: ""
            if (question.isBlank()) {
                Toast.makeText(this, "Enter a question", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            askQuestion(question, lang)
        }
    }

    private fun askQuestion(question: String, language: String) {
        setLoading(true)
        binding.answerText.text = ""
        binding.sourceText.text = ""
        api.ask(AskRequest(question, language)).enqueue(object : Callback<AskResponse> {
            override fun onResponse(call: Call<AskResponse>, response: Response<AskResponse>) {
                setLoading(false)
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body != null) {
                        binding.answerText.text = body.answer
                        binding.sourceText.text = body.source?.let { "Source: $it" } ?: ""
                    } else {
                        binding.answerText.text = "No response"
                    }
                } else {
                    binding.answerText.text = "Server error: ${response.code()}"
                }
            }
            override fun onFailure(call: Call<AskResponse>, t: Throwable) {
                setLoading(false)
                binding.answerText.text = "Network error: ${t.localizedMessage}"
            }
        })
    }

    private fun setLoading(loading: Boolean) {
        binding.progress.visibility = if (loading) View.VISIBLE else View.GONE
        binding.askButton.isEnabled = !loading
    }
}
