package com.pharmagraph.app.domain

import android.graphics.Bitmap

interface PrescriptionTextExtractor {
    suspend fun extract(image: Bitmap): String
}

interface DrugExtractor {
    suspend fun extractDrugs(ocrText: String): List<DrugCandidate>
}

interface DrugVerifier {
    suspend fun verify(candidates: List<DrugCandidate>, rawOcrText: String): List<DrugCandidate>
}

interface DrugNormalizer {
    suspend fun normalize(candidates: List<DrugCandidate>): List<DrugCandidate>
}

interface SlmEngine {
    suspend fun generateStructured(prompt: String): String
}
