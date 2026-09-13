package com.pharmagraph.app.domain

import android.net.Uri
import com.pharmagraph.app.logic.AnalysisResult
import com.pharmagraph.app.logic.RiskLevel

data class PrescriptionSession(
    val imageUri: Uri? = null,
    val rawOcrText: String? = null,
    val candidates: List<DrugCandidate> = emptyList(),
    val verifiedDrugs: List<DrugCandidate> = emptyList(),
    val analysisResult: AnalysisResult? = null,
    val selectedLanguage: String = "English",
    val isProcessing: Boolean = false,
    val error: String? = null,
    val requestId: String = ""
)

data class AnalysisRequest(
    val imageUri: Uri,
    val language: String,
    val timestamp: Long = System.currentTimeMillis()
)

data class MedicationSchedule(
    val drugName: String,
    val dosage: String,
    val windowName: String, // "Morning", "Afternoon", "Night"
    val windowStart: String, // "08:00"
    val windowEnd: String,   // "10:00"
    val guardianPhone: String
)
