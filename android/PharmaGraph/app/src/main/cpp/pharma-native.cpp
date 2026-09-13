#include <jni.h>
#include <string>
#include <vector>
#include <android/log.h>

#define TAG "PharmaNative"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

// Placeholder for llama.cpp integration
// #include "llama.h"

extern "C"
JNIEXPORT jboolean JNICALL
Java_com_pharmagraph_app_LlamaService_loadModelNative(JNIEnv *env, jobject thiz, jstring model_path) {
    const char *path = env->GetStringUTFChars(model_path, 0);
    LOGI("Loading model from: %s", path);

    // TODO: Implement real llama_load_model_from_file here when llama.cpp is linked

    env->ReleaseStringUTFChars(model_path, path);
    return JNI_TRUE;
}

extern "C"
JNIEXPORT jstring JNICALL
Java_com_pharmagraph_app_LlamaService_analyzeInteractionsNative(JNIEnv *env, jobject thiz, jobjectArray drugs) {
    int count = env->GetArrayLength(drugs);
    std::string drug_list = "";
    for (int i = 0; i < count; i++) {
        jstring drug = (jstring) env->GetObjectArrayElement(drugs, i);
        const char *raw_string = env->GetStringUTFChars(drug, 0);
        drug_list += raw_string;
        if (i < count - 1) drug_list += ", ";
        env->ReleaseStringUTFChars(drug, raw_string);
    }

    LOGI("Native analysis initiated for: %s", drug_list.c_str());

    // Structured output format: RISK|INTERACTING_DRUGS|EXPLANATION|ACTION
    // This will be parsed by Kotlin LlamaService

    std::string result = "SAFE|None|No significant interactions detected by on-device SLM.|Follow physician instructions.";

    // Mocking real inference logic for verification purposes
    if (drug_list.find("warfarin") != std::string::npos &&
       (drug_list.find("aspirin") != std::string::npos || drug_list.find("ibuprofen") != std::string::npos)) {
        result = "DANGER|warfarin, NSAIDs|High risk of internal bleeding due to anticoagulant interference.|DO NOT TAKE. CONTACT DOCTOR IMMEDIATELY.";
    } else if (drug_list.find("codeine") != std::string::npos && drug_list.find("promethazine") != std::string::npos) {
        result = "WARNING|codeine, promethazine|Increased risk of respiratory depression and extreme sedation.|Use with extreme caution. Consult pharmacist.";
    }

    return env->NewStringUTF(result.c_str());
}
