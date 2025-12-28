package com.deeni.qa

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    private val executor = Executors.newSingleThreadExecutor()
    private val handler = Handler(Looper.getMainLooper())

    private lateinit var languageSpinner: Spinner
    private lateinit var questionInput: EditText
    private lateinit var askButton: Button
    private lateinit var progress: ProgressBar
    private lateinit var answerText: TextView
    private lateinit var sourceText: TextView
    private lateinit var baseUrlInput: EditText
    private lateinit var saveButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        languageSpinner = findViewById(R.id.languageSpinner)
        questionInput = findViewById(R.id.questionInput)
        askButton = findViewById(R.id.askButton)
        progress = findViewById(R.id.progress)
        answerText = findViewById(R.id.answerText)
        sourceText = findViewById(R.id.sourceText)
        baseUrlInput = findViewById(R.id.baseUrlInput)
        saveButton = findViewById(R.id.saveBaseUrl)

        val prefs = getSharedPreferences("deeniqa_prefs", MODE_PRIVATE)
        val baseUrl = prefs.getString("base_url", "http://10.0.2.2:8000/") ?: "http://10.0.2.2:8000/"
        baseUrlInput.setText(baseUrl)

        val languages = arrayOf("urdu", "english")
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, languages)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        languageSpinner.adapter = adapter

        saveButton.setOnClickListener {
            val url = baseUrlInput.text.toString().trim()
            if (url.isNotEmpty()) {
                prefs.edit().putString("base_url", url).apply()
                Toast.makeText(this, "Base URL saved", Toast.LENGTH_SHORT).show()
            }
        }

        askButton.setOnClickListener {
            val lang = languageSpinner.selectedItem.toString()
            val question = questionInput.text.toString().trim()
            if (question.isEmpty()) {
                Toast.makeText(this, "Enter a question", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            askQuestion(question, lang)
        }
    }

    private fun askQuestion(question: String, language: String) {
        setLoading(true)
        answerText.text = ""
        sourceText.text = ""

        executor.execute {
            try {
                val prefs = getSharedPreferences("deeniqa_prefs", MODE_PRIVATE)
                val baseUrl = prefs.getString("base_url", "http://10.0.2.2:8000/") ?: "http://10.0.2.2:8000/"
                val url = URL(baseUrl + "ask")
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "POST"
                conn.setRequestProperty("Content-Type", "application/json")
                conn.doOutput = true

                val json = JSONObject()
                json.put("question", question)
                json.put("language", language)

                val writer = OutputStreamWriter(conn.outputStream)
                writer.write(json.toString())
                writer.flush()
                writer.close()

                val responseCode = conn.responseCode
                if (responseCode == 200) {
                    val reader = BufferedReader(InputStreamReader(conn.inputStream))
                    val response = reader.readText()
                    reader.close()

                    val jsonResponse = JSONObject(response)
                    val answer = jsonResponse.getString("answer")
                    val source = if (jsonResponse.has("source")) jsonResponse.getString("source") else null

                    handler.post {
                        setLoading(false)
                        answerText.text = answer
                        sourceText.text = if (source != null) "Source: $source" else ""
                    }
                } else {
                    handler.post {
                        setLoading(false)
                        answerText.text = "Server error: $responseCode"
                    }
                }
            } catch (e: Exception) {
                handler.post {
                    setLoading(false)
                    answerText.text = "Network error: ${e.message}"
                }
            }
        }
    }

    private fun setLoading(loading: Boolean) {
        progress.visibility = if (loading) View.VISIBLE else View.GONE
        askButton.isEnabled = !loading
    }
}
