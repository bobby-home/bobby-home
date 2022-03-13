#include <bits/stdint-uintn.h>
#include <cstddef>
#include <vector>
#include <memory>
#include <fstream>
#include <iostream>
#include <string>
#include <regex>
#include <algorithm>

#include <opencv2/opencv.hpp>
#include "tensorflow/lite/builtin_op_data.h"
#include "tensorflow/lite/c/common.h"
#include "tensorflow/lite/interpreter.h"
#include "tensorflow/lite/kernels/register.h"

#include "object_detect.hpp"
#include "object_detection.hpp"


void ObjectDetection::readLabelsFile(const std::string &file_name)
{
	std::ifstream file(file_name);
	if (!file) {
		throw std::runtime_error("ObjectDetection: Failed to load labels file");
    }

	std::string line;
	//std::getline(file, line); // discard first line of ???

	while (std::getline(file, line)) {
        std::regex rgx("([0-9]+)\\s+([a-z]+)");
        std::smatch match;

        if (std::regex_search(line, match, rgx)) {
            unsigned int index = std::stoi(match[1]);
            //std::cout << "id: " << match[1] << " -> " << match[2] << std::endl;
            labels_[index] = match[2];
            //for (auto m : match) {
            //    std::cout << "  submatch '" << m << "'" << '\n';
            //}
        }
        //labels_.push_back(line);
    }

	label_count_ = labels_.size();
    std::cout << "Loaded " << label_count_ << " labels from file " << file_name << std::endl;
}

void ObjectDetection::verifyOutputTensor() {
    // Check the tensor outputs
    int output = interpreter_->outputs()[0];
    TfLiteIntArray *output_dims = interpreter_->tensor(output)->dims;
    // Causes might include loading the wrong model.
    if (output_dims->size != 3 ||
            output_dims->data[0] != 1 ||
            output_dims->data[1] != 10 ||
            output_dims->data[2] != 4) {
        throw std::runtime_error("ObjectDetectTfStage: unexpected output dimensions");
    } else {
        std::cout << "Interpreter output tensor dimensions OK" << std::endl;
    }
}

void ObjectDetection::verifyInputTensor()
{
    // Make an attempt to verify that the model expects this size of input.
    int input = interpreter_->inputs()[0];
    size_t size = interpreter_->tensor(input)->bytes;
    input_layer_size_ = size;

    size_t pixel_size;
    if (interpreter_->tensor(input)->type == kTfLiteUInt8) {
        std::cout << "uses uint8_t" << std::endl;
        pixel_size = sizeof(uint8_t);
    }
    else if (interpreter_->tensor(input)->type == kTfLiteFloat32) {
        throw std::runtime_error("Float tensor is not supported yet.");
        //std::cout << "uses float" << std::endl;
        //pixel_size = sizeof(float);
    }
    else {
        throw std::runtime_error("TfStage: Input tensor data type not supported");
    }

    size_t check = tf_w_ * tf_h_ *nb_channels_ * pixel_size;

    if (check != size) {
        std::cout << "tf_w = tf_h = " << tf_h_ << tf_w_ << std::endl;
        std::cout << "Input size: " << check << " expected tf tensor size: " << size << std::endl;
        std::cout << "pixel size=" << pixel_size << std::endl;
        throw std::runtime_error("TfStage: Input tensor size mismatch between input and expected tf tensor.");
    } else {
        std::cout << "Input tensor dimensions ok. Expect " << size << " bytes." << std::endl;
    }
}

void ObjectDetection::init()
{
	model_ = tflite::FlatBufferModel::BuildFromFile(config_->model_file.c_str());
	if (!model_) {
		throw std::runtime_error("TfStage: Failed to load model");
	}
	std::cout << "TfStage: Loaded model " << config_->model_file << std::endl;

	tflite::ops::builtin::BuiltinOpResolver resolver;
	tflite::InterpreterBuilder(*model_, resolver)(&interpreter_);
	if (!interpreter_) {
		throw std::runtime_error("TfStage: Failed to construct interpreter");
	}

	if (config_->number_of_threads > 0) {
        std::cout << "Set the tf interpreter num threads to " << config_->number_of_threads << std::endl;
		interpreter_->SetNumThreads(config_->number_of_threads);
	} else {
        std::cout << "Number of threads <= 0, ignoring this configuration." << std::endl;
    }

	if (interpreter_->AllocateTensors() != kTfLiteOk) {
		throw std::runtime_error("TfStage: Failed to allocate tensors");
	}

    verifyInputTensor();
    verifyOutputTensor();
}

//void ObjectDetection::runInference(std::vector<std::uint8_t> rgb_image)
//void ObjectDetection::runInference(uint8_t* rgb_image, size_t size)
void ObjectDetection::runInference(cv::Mat& img_matrice, std::vector<Detection> &detections)
{
    cv::resize(img_matrice, img_matrice, cv::Size(tf_w_, tf_h_));
    cv::cvtColor(img_matrice, img_matrice, cv::COLOR_BGR2RGB);

    int input = interpreter_->inputs()[0];

	if (interpreter_->tensor(input)->type == kTfLiteUInt8)
	{
        // flatten rgb image to input layer.
		uint8_t *inputLayer = interpreter_->typed_tensor<uint8_t>(input);

        // overflow: size is computed from tf_h, tf_w assuming its RGB.
        // before this the image is converted to RGB and resized using tf_h & th_w.
        // -> ok and we use the tf inputLayer size to be sure.
		memcpy(inputLayer, img_matrice.ptr<uint8_t>(0), input_layer_size_);

        // if you have a vector<uint8_t>
        //for (unsigned int i = 0; i < rgb_image.size(); i++) {
		//	tensor[i] = rgb_image[i];
		//}
	}
	else if (interpreter_->tensor(input)->type == kTfLiteFloat32)
	{
		throw std::runtime_error("Float tensor is not supported yet.");
	} else
    {
		throw std::runtime_error("Unkown input tensor type. Can't handle it");
	}

	if (interpreter_->Invoke() != kTfLiteOk) {
		throw std::runtime_error("TfStage: Failed to invoke TFLite");
	}

	interpretOutputs(detections);
}

void ObjectDetection::interpretOutputs(std::vector<Detection> &detections)
{
	int box_index = interpreter_->outputs()[0];
	int class_index = interpreter_->outputs()[1];
	int score_index = interpreter_->outputs()[2];
	int num_detections = interpreter_->tensor(box_index)->dims->data[1];

    float *boxes = interpreter_->tensor(box_index)->data.f;
	float *scores = interpreter_->tensor(score_index)->data.f;
	float *classes = interpreter_->tensor(class_index)->data.f;

	for (int i = 0; i < num_detections; i++) {
		int c = classes[i];

		if (scores[i] < config_->confidence_threshold) {
            if (config_->verbose) {
                //std::cout << "Found something below the confidence_threshold: " << scores[i] << " label id:" << c << " -> " << labels_[c] << std::endl;
            }
            continue;
        }

		// The coords in the tf_w_ x tf_h_ image fed to the network are:
		int y = std::clamp<int>(tf_h_ * boxes[i * 4 + 0], 0, tf_h_);
		int x = std::clamp<int>(tf_w_ * boxes[i * 4 + 1], 0, tf_w_);
		int h = std::clamp<int>(tf_h_ * boxes[i * 4 + 2] - y, 0, tf_h_);
		int w = std::clamp<int>(tf_w_ * boxes[i * 4 + 3] - x, 0, tf_w_);

		// The network is fed a crop from the lores (if that was too large), so the coords
		// in the full lores image are:
		// @todo: find what are these "lores_info" shit.
        //y += (lores_info_.tf_h_ - tf_h_) / 2;
		//x += (lores_info_.width - tf_w_) / 2;
		// The lores is a pure scaling of the main image (squishing if the aspect ratios
		// don't match), so:
		//y = y * main_stream_info_.height / lores_info_.height;
		//x = x * main_stream_info_.width / lores_info_.width;
		//h = h * main_stream_info_.height / lores_info_.height;
		//w = w * main_stream_info_.width / lores_info_.width;

		Detection detection(c, labels_[c], scores[i], x, y, w, h);
        detections.push_back(detection);
        std::cout << "detected somebody " << scores[i] << " label id:" << c << " -> " << labels_[c] << std::endl;
        std::cout << "-------" << std::endl;
	}

	//if (config_->verbose)
	if (false)
    {
		for (auto &detection : detections)
			std::cerr << detection.toString() << std::endl;
	}
}

