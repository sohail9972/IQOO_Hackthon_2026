package com.pharmagraph.app

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File

class LlamaService(private val context: Context) {

    data class AnalysisResult(
        val riskLevel: String,
        val interactingDrugs: String,
        val explanation: String,
        val recommendedAction: String
    )

    companion object {
        init {
            System.loadLibrary("pharma-native")
        }
    }

    private var isModelLoaded = false

    suspend fun initialize(modelPath: String): Boolean = withContext(Dispatchers.IO) {
        if (isModelLoaded) return@withContext true
        
        val file = File(modelPath)
        if (!file.exists()) return@withContext false
        
        isModelLoaded = loadModelNative(modelPath)
        isModelLoaded
    }

    suspend fun analyze(drugs: List<String>): AnalysisResult = withContext(Dispatchers.IO) {
        val rawResult = analyzeInteractionsNative(drugs.toTypedArray())
        parseResult(rawResult)
    }

    private fun parseResult(raw: String): AnalysisResult {
        val parts = raw.split("|")
        return if (parts.size >= 4) {
            AnalysisResult(parts[0], parts[1], parts[2], parts[3])
        } else {
            AnalysisResult("ERROR", "Unknown", "Malformed model output", "Retry or consult professional")
        }
    }

    private external fun loadModelNative(modelPath: String): Boolean
    private external fun analyzeInteractionsNative(drugs: Array<String>): String
}
