package com.pharmagraph.app

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.speech.tts.TextToSpeech
import android.telephony.SmsManager
import android.view.View
import android.widget.*
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.pharmagraph.app.domain.VerificationStatus
import com.pharmagraph.app.logic.PipelineState
import com.pharmagraph.app.logic.RiskLevel
import com.pharmagraph.app.logic.AnalysisResult
import com.pharmagraph.app.logic.PrescriptionViewModel
import kotlinx.coroutines.launch
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : AppCompatActivity(), TextToSpeech.OnInitListener {

    private lateinit var tts: TextToSpeech
    private lateinit var drugInput: EditText
    private lateinit var resultText: TextView
    private lateinit var statusText: TextView
    private lateinit var btnSpeak: Button
    private lateinit var imagePreview: ImageView
    private lateinit var languageSpinner: Spinner
    private lateinit var guardianNumberInput: EditText
    
    private val viewModel: PrescriptionViewModel by viewModels()
    private lateinit var llamaService: LlamaService
    private val templateProvider = WarningTemplateProvider()
    
    private var isTtsInitialized = false
    private val PREFS_NAME = "PharmaGraphPrefs"
    private val KEY_GUARDIAN = "guardian_number"
    private val KEY_LANGUAGE = "selected_language"

    private var currentPhotoPath: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        llamaService = LlamaService(this)
        
        initViews()
        setupLanguageSpinner()
        loadSettings()
        
        tts = TextToSpeech(this, this)
        
        // Runtime permissions request for camera, sms and storage
        ActivityCompat.requestPermissions(this, arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.SEND_SMS,
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE
        ), 100)
        
        setupObservers()

        lifecycleScope.launch {
            llamaService.initialize("/sdcard/Download/model.gguf")
        }
    }

    private fun initViews() {
        drugInput = findViewById(R.id.drugInput)
        resultText = findViewById(R.id.resultText)
        statusText = findViewById(R.id.statusText)
        btnSpeak = findViewById(R.id.btnSpeak)
        imagePreview = findViewById(R.id.imagePreview)
        languageSpinner = findViewById(R.id.languageSpinner)
        guardianNumberInput = findViewById(R.id.guardianNumberInput)
        
        val btnScan = findViewById<Button>(R.id.btnScan)
        val btnAnalyze = findViewById<Button>(R.id.btnAnalyze)

        btnScan.setOnClickListener {
            dispatchTakePictureIntent()
        }

        btnAnalyze.setOnClickListener {
            saveSettings()
            analyzeDrugs()
        }

        btnSpeak.setOnClickListener {
            speakWarning()
        }
    }

    private fun setupObservers() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    when (state) {
                        is PipelineState.Idle -> {
                            statusText.text = "Ready to scan prescription."
                        }
                        is PipelineState.Processing -> {
                            statusText.text = "Processing prescription... (OCR -> Extraction -> Verification)"
                        }
                        is PipelineState.Success -> {
                            val result = state.result
                            val analysis = state.analysis

                            statusText.text = "Prescription detected and verified."

                            val displayBuilder = StringBuilder()
                            displayBuilder.append("Detected Medications:\n\n")

                            result.verifiedDrugs.forEach { drug ->
                                val icon = when (drug.verificationStatus) {
                                    VerificationStatus.GREEN -> "✓"
                                    VerificationStatus.YELLOW -> "⚠"
                                    VerificationStatus.RED -> "✗"
                                }
                                displayBuilder.append("$icon ${drug.rawName} — ${drug.verificationStatus}\n")
                            }

                            if (analysis != null) {
                                displayBuilder.append("\n--- Analysis ---\n")
                                displayBuilder.append(analysis.warningText)
                            }

                            resultText.text = displayBuilder.toString()

                            if (analysis?.riskLevel == RiskLevel.DANGER) {
                                speakWarning()
                                sendGuardianSms(analysis.warningText)
                            }
                        }
                        is PipelineState.Error -> {
                            statusText.text = "Error: ${state.message}"
                            Toast.makeText(this@MainActivity, state.message, Toast.LENGTH_LONG).show()
                        }
                    }
                }
            }
        }
    }

    private fun dispatchTakePictureIntent() {
        Intent(MediaStore.ACTION_IMAGE_CAPTURE).also { takePictureIntent ->
            takePictureIntent.resolveActivity(packageManager)?.also {
                val photoFile: File? = try {
                    createImageFile()
                } catch (ex: IOException) {
                    Toast.makeText(this, "File creation error: ${ex.message}", Toast.LENGTH_SHORT).show()
                    null
                }
                photoFile?.also {
                    val photoURI: Uri = FileProvider.getUriForFile(
                        this,
                        "com.pharmagraph.app.fileprovider",
                        it
                    )
                    takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI)
                    startActivityForResult(takePictureIntent, 102)
                }
            }
        }
    }

    @Throws(IOException::class)
    private fun createImageFile(): File {
        val timeStamp: String = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
        val storageDir: File? = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return File.createTempFile("JPEG_${timeStamp}_", ".jpg", storageDir).apply {
            currentPhotoPath = absolutePath
        }
    }

    private fun setupLanguageSpinner() {
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, templateProvider.getLanguages())
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        languageSpinner.adapter = adapter
        
        languageSpinner.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val selectedLang = templateProvider.getLanguages()[position]
                updateTtsLanguage(selectedLang)
            }
            override fun onNothingSelected(parent: AdapterView<*>?) {}
        }
    }

    private fun loadSettings() {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        guardianNumberInput.setText(prefs.getString(KEY_GUARDIAN, ""))
        val savedLang = prefs.getString(KEY_LANGUAGE, "English")
        val position = templateProvider.getLanguages().indexOf(savedLang)
        if (position >= 0) languageSpinner.setSelection(position)
    }

    private fun saveSettings() {
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        prefs.edit().apply {
            putString(KEY_GUARDIAN, guardianNumberInput.text.toString())
            putString(KEY_LANGUAGE, languageSpinner.selectedItem.toString())
            apply()
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        if (requestCode == 102 && resultCode == RESULT_OK) {
            val bitmap = currentPhotoPath?.let { BitmapFactory.decodeFile(it) }

            if (bitmap != null) {
                imagePreview.setImageBitmap(bitmap)
                statusText.text = "Processing prescription... (OCR -> Extraction -> Verification)"

                val selectedLanguage = languageSpinner.selectedItem.toString().lowercase()
                val langCode = when (selectedLanguage) {
                    "tamil" -> "ta"
                    "hindi" -> "hi"
                    "kannada" -> "kn"
                    "telugu" -> "te"
                    "english" -> "en"
                    else -> "en"
                }
                
                updateTtsLanguage(languageSpinner.selectedItem.toString())
                viewModel.processPrescription(bitmap, langCode)
            } else {
                statusText.text = "Failed to load captured image"
            }
        }
    }

    private fun analyzeDrugs() {
        val drugs = drugInput.text.toString().split("\n")
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            
        if (drugs.isEmpty()) {
            Toast.makeText(this, "Please enter drug names", Toast.LENGTH_SHORT).show()
            return
        }

        statusText.text = "Running on-device SLM analysis..."
        lifecycleScope.launch {
            val result = llamaService.analyze(drugs)
            displayInteractionResult(result)
        }
    }

    private fun displayInteractionResult(result: LlamaService.AnalysisResult) {
        val selectedLang = languageSpinner.selectedItem.toString()
        val formattedWarning = templateProvider.formatWarning(selectedLang, result)
        
        resultText.text = formattedWarning
        btnSpeak.isEnabled = true
        statusText.text = "Analysis complete."

        if (result.riskLevel.uppercase() == "DANGER") {
            speakWarning()
            sendGuardianSms(formattedWarning)
        }
    }

    private fun sendGuardianSms(message: String) {
        val guardianNumber = getSharedPreferences("PharmaGraphPrefs", MODE_PRIVATE)
            .getString("guardian_number", "")
        
        if (guardianNumber.isNullOrEmpty()) {
            Toast.makeText(this, "Set guardian number in settings", Toast.LENGTH_LONG).show()
            return
        }
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.SEND_SMS)
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.SEND_SMS), 200)
            return
        }
        
        try {
            val smsManager = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                getSystemService(SmsManager::class.java)
            } else {
                @Suppress("DEPRECATION")
                SmsManager.getDefault()
            }
            val parts = smsManager.divideMessage(
                "URGENT: PharmaGraph detected dangerous drug interactions. $message"
            )
            smsManager.sendMultipartTextMessage(guardianNumber, null, parts, null, null)
            Toast.makeText(this, "SMS sent to $guardianNumber", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            Toast.makeText(this, "SMS failed: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun speakWarning() {
        if (isTtsInitialized) {
            val selectedLanguage = languageSpinner.selectedItem.toString().lowercase()
            val locale = when (selectedLanguage) {
                "tamil" -> Locale("ta", "IN")
                "hindi" -> Locale("hi", "IN")
                "kannada" -> Locale("kn", "IN")
                "telugu" -> Locale("te", "IN")
                else -> Locale("en", "IN")
            }
            tts.language = locale
            tts.speak(resultText.text.toString(), TextToSpeech.QUEUE_FLUSH, null, "WarningID")
        } else {
            Toast.makeText(this, "TTS not ready", Toast.LENGTH_SHORT).show()
        }
    }

    private fun updateTtsLanguage(languageName: String) {
        if (!isTtsInitialized) return
        val selectedLanguage = languageName.lowercase()
        val locale = when (selectedLanguage) {
            "tamil" -> Locale("ta", "IN")
            "hindi" -> Locale("hi", "IN")
            "kannada" -> Locale("kn", "IN")
            "telugu" -> Locale("te", "IN")
            else -> Locale("en", "IN")
        }
        val result = tts.setLanguage(locale)
        if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
            Toast.makeText(this, "$languageName not supported on this device", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            isTtsInitialized = true
            updateTtsLanguage(languageSpinner.selectedItem.toString())
        } else {
            Toast.makeText(this, "TTS Init failed", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onDestroy() {
        if (::tts.isInitialized) {
            tts.stop()
            tts.shutdown()
        }
        super.onDestroy()
    }
}
