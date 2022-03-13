#include <cstddef>
#include <map>
#include <unordered_map>
#include <vector>
#include <memory>
#include <fstream>
#include <iostream>

#include <opencv2/imgproc.hpp>
#include "object_detect.hpp"

constexpr uint CHANNEL = 3;
#define NAME "object_detection"
#define DEFAULT_CONFIDENCE_TRHESHOLD 0.6


// The TfStage is a convenient base class from which post processing stages using
// TensorFlowLite can be derived. It provides a certain amount of boiler plate code
// and some other useful functions. Please refer to the examples provided that make
// use of it.
struct TfConfig
{
    int number_of_threads = 3;
    std::string model_file;
    bool verbose = false;
};

struct ObjectDetectTfConfig : public TfConfig
{
    float confidence_threshold = DEFAULT_CONFIDENCE_TRHESHOLD;
};

class ObjectDetection
{
public:
    // The constructor supplies the width and height that TFLite wants.
	ObjectDetection(int tf_w, int tf_h, const std::string& labels_file, const std::string& model_file)
	{
        std::cout << "Initializing ObjectDetection tf_w=" << tf_w << " tf_h=" << tf_h << std::endl;
        tf_h_ = tf_h;
        tf_w_ = tf_w;

        // we only works with RGB for now.
        nb_channels_ = 3;
        config_ = std::make_unique<ObjectDetectTfConfig>();

        config_->model_file = model_file;
        config_->verbose = true;
        readLabelsFile(labels_file);
		init();
	}
	char const *Name() const { return NAME; }

    //void runInference(std::vector<std::uint8_t> rgb_image);
    //void runInference(uint8_t* rgb_image, size_t size);
    void runInference(cv::Mat& img_matrice, std::vector<Detection> &detections);
private:
    void interpretOutputs(std::vector<Detection> &detections);
	void readLabelsFile(const std::string &file_name);

    // labels read from the labels file.
	//std::vector<std::string> labels_;
    std::unordered_map<unsigned int, std::string> labels_;
	size_t label_count_;

    unsigned int tf_w_, tf_h_, nb_channels_;
    size_t input_layer_size_;
    std::unique_ptr<ObjectDetectTfConfig> config_;

    std::unique_ptr<tflite::FlatBufferModel> model_;
	std::unique_ptr<tflite::Interpreter> interpreter_;
    void init();
    void verifyInputTensor();
    void verifyOutputTensor();
};

