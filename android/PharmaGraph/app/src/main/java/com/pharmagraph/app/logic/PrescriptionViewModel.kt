package com.pharmagraph.app.logic

import android.graphics.Bitmap
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.pharmagraph.app.infrastructure.MlKitPrescriptionTextExtractor
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import com.pharmagraph.app.logic.AnalysisResult
import com.pharmagraph.app.logic.TrustedPairAnalyzer


sealed class PipelineState {
    object Idle : PipelineState()
    object Processing : PipelineState()
    data class Success(
        val result: PrescriptionExtractionResult,
        val analysis: AnalysisResult? = null
    ) : PipelineState()
    data class Error(val message: String) : PipelineState()
}

class PrescriptionViewModel : ViewModel() {

    private val pipeline = PrescriptionAnalysisPipeline(
        textExtractor = MlKitPrescriptionTextExtractor(),
        drugExtractor = StageADrugExtractor(),
        drugVerifier = DeterministicDrugVerifier()
    )

    private val analyzer = TrustedPairAnalyzer()

    private val _uiState = MutableStateFlow<PipelineState>(PipelineState.Idle)
    val uiState: StateFlow<PipelineState> = _uiState

    fun processPrescription(bitmap: Bitmap, language: String = "ta") {
        viewModelScope.launch {
            _uiState.value = PipelineState.Processing
            try {
                val result = pipeline.process(bitmap)
                val analysis = analyzer.analyze(result.verifiedDrugs, language)
                _uiState.value = PipelineState.Success(result, analysis)
            } catch (e: Exception) {
                _uiState.value = PipelineState.Error(e.message ?: "Unknown error")
            }
        }
    }
}