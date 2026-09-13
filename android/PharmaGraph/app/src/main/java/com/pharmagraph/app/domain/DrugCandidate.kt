package com.pharmagraph.app.domain

enum class VerificationStatus {
    GREEN, YELLOW, RED
}

data class DrugCandidate(
    val rawName: String,
    val normalizedName: String? = null,
    val confidence: Float = 0f,
    val verificationStatus: VerificationStatus = VerificationStatus.RED,
    val sourceText: String = "",
    val possibleMatches: List<String> = emptyList(),
    val reason: String = ""
)
