package com.pharmagraph.app.logic

import android.graphics.Bitmap
import com.pharmagraph.app.domain.*

data class PrescriptionExtractionResult(
    val rawText: String,
    val candidates: List<DrugCandidate>,
    val verifiedDrugs: List<DrugCandidate>
)

class PrescriptionAnalysisPipeline(
    private val textExtractor: PrescriptionTextExtractor,
    private val drugExtractor: DrugExtractor,
    private val drugVerifier: DrugVerifier
) {
    suspend fun process(image: Bitmap): PrescriptionExtractionResult {
        val rawText = textExtractor.extract(image)
        val candidates = drugExtractor.extractDrugs(rawText)
        val verified = drugVerifier.verify(candidates, rawText)
        
        return PrescriptionExtractionResult(
            rawText = rawText,
            candidates = candidates,
            verifiedDrugs = verified
        )
    }
}
